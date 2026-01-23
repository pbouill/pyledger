from sqlalchemy.ext.associationproxy import association_proxy

class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    # ... other fields ...

    users = association_proxy("company_users", "user")  # <- keep only one definition
    # Remove duplicate 'users' definition

    # ... rest of class ...
