import json
import pathlib

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    select,
)

from canon.util import deduplicate


def test_deduplicate_user_email_dry_run_and_apply(tmp_path: "pathlib.Path") -> None:
    db_file = tmp_path / "dedup.db"
    engine = create_engine(f"sqlite:///{db_file}")

    metadata = MetaData()

    # Create a test table pair (user_dup, company_dup) without UNIQUE constraints
    user_dup = Table(
        "user_dup",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("username", String(150), nullable=False),
        Column("email", String(255), nullable=False),
        Column("password_hash", String(255), nullable=False),
        Column("is_active", Integer, nullable=False, default=1),
        Column("is_admin", Integer, nullable=False, default=0),
    )

    company_dup = Table(
        "company_dup",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("name", String(200), nullable=False),
        Column("primary_contact_id", Integer, ForeignKey("user_dup.id")),
    )

    metadata.create_all(engine)

    # Insert users: two with same email (different ids)
    with engine.connect() as conn:
        conn.execute(
            user_dup.insert(),
            [
                {
                    "username": "u1",
                    "email": "dup@example.com",
                    "password_hash": "x",
                },
                {
                    "username": "u2",
                    "email": "dup@example.com",
                    "password_hash": "y",
                },
                {
                    "username": "unique",
                    "email": "uniq@example.com",
                    "password_hash": "z",
                },
            ],
        )
        conn.commit()

        # Insert a company that references the second duplicate (u2)
        r = conn.execute(select(user_dup).where(user_dup.c.username == "u2")).first()
        assert r is not None
        u2_id = r._mapping["id"]
        conn.execute(
            company_dup.insert(),
            [
                {
                    "name": "TestCo",
                    "primary_contact_id": u2_id,
                }
            ],
        )
        conn.commit()

        # Dry-run: nothing should change
        groups = deduplicate.find_duplicate_groups(engine, "user_dup", "email")
        assert len(groups) == 1
        deduplicate.apply_dedup(engine, "user_dup", "email", dry_run=True)

        # Ensure both users still exist and company still references u2
        users = conn.execute(select(user_dup)).fetchall()
        assert len(users) == 3
        comp = conn.execute(select(company_dup)).first()
        assert comp is not None
        assert comp._mapping["primary_contact_id"] == u2_id

        # Apply dedupe using the same connection so in-memory SQLite sees changes
        deduplicate.apply_dedup(
            engine,
            "user_dup",
            "email",
            dry_run=False,
            connection=conn,
        )

        # After apply, duplicates should be collapsed to canonical (min id)
        with engine.connect() as conn2:
            users_after = conn2.execute(select(user_dup)).fetchall()
            user_emails = [row._mapping["email"] for row in users_after]
            assert user_emails.count("dup@example.com") == 1

            # Company should now point to the canonical id (min of original duplicates)
            canonical_row = conn2.execute(
                select(user_dup).where(
                    user_dup.c.email == "dup@example.com"
                )
            ).first()
            assert canonical_row is not None
            canonical_id = canonical_row._mapping["id"]
            comp_after = conn2.execute(select(company_dup)).first()
            assert comp_after is not None
            assert comp_after._mapping["primary_contact_id"] == canonical_id

        # Archive table should contain the archived duplicate row(s)
        archive_tbl = "user_dup_dedupe_archive"
        res = conn.execute(
            select(
                Table(archive_tbl, MetaData(), autoload_with=engine)
            )
        ).first()
        assert res is not None
        # original_data is stored as JSON string; validate it contains the original id
        od = json.loads(res._mapping["original_data"])
        assert "id" in od
