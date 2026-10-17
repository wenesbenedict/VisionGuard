from getpass import getpass

from . import models
from .database import SessionLocal
from .services.auth import hash_password


def main() -> int:
    email = input("Existing administrator email: ").strip().lower()
    password = getpass("New password (minimum 14 characters): ")
    confirmation = getpass("Confirm new password: ")
    if len(password) < 14:
        print("Password must be at least 14 characters.")
        return 1
    if password != confirmation:
        print("Passwords did not match.")
        return 1

    with SessionLocal() as db:
        user = db.query(models.User).filter(
            models.User.email == email,
            models.User.role == "ADMIN",
        ).first()
        if user is None:
            print("No administrator with that email exists; no changes were made.")
            return 1
        user.password_hash = hash_password(password)
        db.commit()
    print("Administrator password updated. Existing sessions for this account are invalidated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
