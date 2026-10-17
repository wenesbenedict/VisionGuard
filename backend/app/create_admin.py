from getpass import getpass

from . import models
from .database import Base, SessionLocal, engine
from .services.auth import hash_password


def main() -> int:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(models.User).first() is not None:
            print("Administrator bootstrap is disabled because users already exist.")
            print("Existing accounts and records were not changed.")
            return 1

        name = input("Administrator name: ").strip()
        email = input("Administrator email: ").strip().lower()
        password = getpass("New password (minimum 14 characters): ")
        confirmation = getpass("Confirm password: ")
        if not name or "@" not in email:
            print("A name and valid-looking email address are required.")
            return 1
        if len(password) < 14:
            print("Password must be at least 14 characters.")
            return 1
        if password != confirmation:
            print("Passwords did not match.")
            return 1

        db.add(models.User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="ADMIN",
        ))
        db.commit()
    print("Administrator created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
