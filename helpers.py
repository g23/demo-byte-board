from flask import redirect, session

# decorator to require logged in
def require_logged_in(f):
    def wrapped(*args, **kargs):
        if "user_id" not in session:
            return redirect("/")
        # otherwise let it go through
        return f(*args, **kargs) 
    return wrapped
