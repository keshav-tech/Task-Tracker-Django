

# 📌 **README**

## 🚀 Django Task Tracker – Mini Project

This project is a simple Django-based task & project tracking system with session authentication, ORM-based queries, validation rules, and a dashboard summary.

---

## 🔧 **How to Run Migrations & Start the Server**

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

---

## 👤 **How to Create a Test User**

Use Django shell:

```bash
python manage.py shell
```

Then run:

```python
from django.contrib.auth.models import User
User.objects.create_user(username="keshav", password="Password@123")
exit()
```

You can now log in using:

```
username: keshav
password: Password@123
```

---

## 📘 **Project Architecture Summary**

### 📌 **How I Modeled the Data**

* **Project** model includes name, description, owner, timestamps, and a uniqueness constraint (`unique_together`) so each user cannot create two projects with the same name.
* **Task** model stores project relation, title, description, status, due date, priority, timestamps, and an optional assignee (User).
* Validation is done in the `clean()` method to check:

  * priority is between **1–5**
  * tasks marked as **done** cannot have a future due date

---

### 🔐 **How I Protected Access (Auth / Permissions)**

* Authentication uses **Django session login** (`authenticate` + `login()`).
* All API endpoints (except login) require authentication using `@login_required`.
* Only the **project owner** can create tasks inside that project.
* The `/tasks/` endpoint returns:

  * tasks in projects owned by the user
  * tasks assigned to the user

---

### 📊 **How I Implemented the Dashboard Query**

* The dashboard uses **Django ORM aggregation** (`Count`, filtering, and ordering).
* It returns:

  * total number of user-owned projects
  * total number of tasks in those projects
  * number of tasks grouped by status (`values().annotate()`)
  * top 5 upcoming tasks sorted by due date
* If no upcoming tasks exist, it returns the string:

  ```
  "No upcoming tasks!"
  ```

**NOTE: I have implemented the dashboard using ORM aggregation, not manual Python loops.**

---

If you want, I can also generate a **full professional README with sections, formatting, screenshots, and Postman usage instructions**.
