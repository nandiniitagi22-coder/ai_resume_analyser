import urllib.parse

# ---------------- Courses ----------------
ds_course = [
    ["Machine Learning Crash Course (Google) [Free]", "https://developers.google.com/machine-learning/crash-course"],
    ["Machine Learning by Andrew Ng (Coursera)", "https://www.coursera.org/learn/machine-learning"],
    ["Data Scientist with Python (DataCamp)", "https://www.datacamp.com/tracks/data-scientist-with-python"],
]

web_course = [
    ["Django Crash Course [YouTube]", "https://youtu.be/e1IyzVyrLSU"],
    ["React Crash Course [YouTube]", "https://youtu.be/Dorf8i6lCuk"],
    ["Full-Stack Web Dev (Coursera)", "https://www.coursera.org/specializations/full-stack-mobile-app-development"],
]

android_course = [
    ["Android Development for Beginners [YouTube]", "https://youtu.be/fis26HvvDII"],
    ["Android Kotlin Developer (Udacity)", "https://www.udacity.com/course/android-kotlin-developer-nanodegree--nd940"],
]

ios_course = [
    ["iOS & Swift Bootcamp (Udemy)", "https://www.udemy.com/course/ios-13-app-development-bootcamp/"],
    ["iOS Development (LinkedIn Learning)", "https://www.linkedin.com/learning/subscription/topics/ios"],
]

uiux_course = [
    ["UI/UX Design Specialization (Coursera)", "https://www.coursera.org/specializations/ui-ux-design"],
    ["Google UX Design (Coursera)", "https://www.coursera.org/professional-certificates/google-ux-design"],
]

# ---------------- Dynamic YouTube Links ----------------
def get_resume_videos(predicted_field: str, missing_skills: list):
    """
    Returns a list of YouTube URLs for resume tips based on missing skills.
    Each missing skill gets a dedicated search link.
    """
    videos = []
    if missing_skills:
        for skill in missing_skills:
            query = f"{predicted_field} {skill} resume tutorial"
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            videos.append(url)
    else:
        # Fallback if no missing skills: general resume tips for the field
        query = f"{predicted_field} resume tips" if predicted_field else "resume tips"
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        videos.append(url)
    return videos

def get_interview_videos(predicted_field: str):
    """
    Returns a list of YouTube URLs for interview preparation based on predicted field.
    """
    query = f"{predicted_field} interview preparation" if predicted_field else "interview preparation"
    return [f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"]
