import sqlite3
from datetime import datetime
from groq import Groq
from textblob import TextBlob

class MentalHealthChatbot:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is required.")
        self.client = Groq(api_key=api_key)
        self.setup_database()

        self.exercises = {
            "breathing": {
                "title": "Deep Breathing Exercise",
                "description": "Take a deep breath in through your nose for 4 seconds, hold for 4 seconds, and exhale through your mouth for 6 seconds. Repeat for 5 minutes.",
                "visual": "https://i.imgur.com/xyz123.gif",  # Replace with a real image URL
                "video_link": "https://youtu.be/X4Y-py3Axyk?si=ZHomRCeT6I2sOm6H"  # Replace with a real video URL
            },
            "mindfulness": {
                "title": "5-Minute Mindfulness Exercise",
                "description": "Sit comfortably, close your eyes, and focus on your breath. Notice the sensations of each inhale and exhale. If your mind wanders, gently bring it back to your breath.",
                "visual": "https://i.imgur.com/abc456.jpg",  # Replace with a real image URL
                "video_link": "https://www.youtube.com/watch?v=example_mindfulness"  # Replace with a real video URL
            },
            "cbt": {
                "title": "Cognitive Behavioral Therapy (CBT) Technique",
                "description": "Identify a negative thought, challenge its validity, and replace it with a more balanced thought. Write down your thoughts and reflect on them.",
                "visual": "https://i.imgur.com/def789.png",  # Replace with a real image URL
                "video_link": "https://www.youtube.com/watch?v=example_cbt"  # Replace with a real video URL
            }
        }
    
    def get_exercise(self, exercise_type):
        """
        Retrieve an exercise based on the type (breathing, mindfulness, cbt).
        """
        exercise = self.exercises.get(exercise_type)
        if not exercise:
            return "Exercise not found. Please try again."

        response = f"""
        <strong>{exercise['title']}</strong><br>
        {exercise['description']}<br>
        <img src="{exercise['visual']}" alt="{exercise['title']}" style="max-width: 100%; height: auto;"><br>
        <a href="{exercise['video_link']}" target="_blank">Watch Video</a>
        """
        return response


    def setup_database(self):
        """
        Set up the SQLite database to store mood logs.
        """
        self.conn = sqlite3.connect("mood_tracker.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mood_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                mood TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def log_mood(self, user_id, mood):
        """
        Log the user's mood in the database.
        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO mood_logs (user_id, mood, date)
            VALUES (?, ?, ?)
        """, (user_id, mood, date))
        self.conn.commit()
        return f"Mood logged: {mood} on {date}"

    def get_mood_insights(self, user_id):
        """
        Analyze the user's mood logs and provide insights.
        """
        self.cursor.execute("""
            SELECT mood, COUNT(*) as count
            FROM mood_logs
            WHERE user_id = ?
            GROUP BY mood
            ORDER BY count DESC
        """, (user_id,))
        mood_counts = self.cursor.fetchall()

        if not mood_counts:
            return "No mood logs found. Start logging your mood to get insights!"

        insights = []
        for mood, count in mood_counts:
            insights.append(f"{mood}: {count} times")

        return "Here are your mood insights:\n" + "\n".join(insights)

    def detect_sentiment(self, text):
        """
        Analyze the sentiment of the user's input using TextBlob.
        Returns: 'positive', 'negative', or 'neutral'
        """
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity

        if polarity > 0:
            return "positive"
        elif polarity < 0:
            return "negative"
        else:
            return "neutral"

    def get_motivational_quote(self, user_input):
        """
        Provide a personalized motivational quote based on the user's mood.
        """
        sentiment = self.detect_sentiment(user_input)
        import random
        quote = random.choice(self.quotes.get(sentiment, ["Stay strong and keep going!"]))
        return f"Here's a motivational quote for you:\n\n{quote}"

    def generate_response(self, user_input, user_id):
        """
        Generate a response based on the user's input.
        """
        # Check if the user wants to log their mood
        if user_input.startswith("/log_mood"):
            mood = user_input.split(" ", 1)[1].strip()
            return {
                "response": self.log_mood(user_id, mood),
                "sentiment": "neutral"  # Default sentiment for mood logging
            }

        # Check if the user wants mood insights
        if user_input.strip().lower() == "/mood_insights":
            return {
                "response": self.get_mood_insights(user_id),
                "sentiment": "neutral"  # Default sentiment for mood insights
            }

        # Check if the user wants an exercise
        if user_input.strip().lower() == "/breathing_exercise":
            return {
                "response": self.get_exercise("breathing"),
                "sentiment": "neutral"  # Default sentiment for exercises
            }
        if user_input.strip().lower() == "/mindfulness":
            return {
                "response": self.get_exercise("mindfulness"),
                "sentiment": "neutral"  # Default sentiment for exercises
            }
        if user_input.strip().lower() == "/cbt_technique":
            return {
                "response": self.get_exercise("cbt"),
                "sentiment": "neutral"  # Default sentiment for exercises
            }

        # Detect sentiment
        sentiment = self.detect_sentiment(user_input)

        # Customize the prompt based on sentiment
        if sentiment == "negative":
            prompt = f"""
            The user seems to be feeling negative. They have shared the following: {user_input}
            Please respond in a way that is empathetic, supportive, and understanding.
            """
        elif sentiment == "positive":
            prompt = f"""
            The user seems to be feeling positive. They have shared the following: {user_input}
            Please respond in a way that is encouraging and uplifting.
            """
        else:
            prompt = f"""
            The user seems to be feeling neutral. They have shared the following: {user_input}
            Please respond in a way that is friendly and engaging.
            """

        # Generate a response using the Groq API
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="mixtral-8x7b-32768",  # Use the appropriate model
        )

        # Extract the response and include the sentiment
        return {
            "response": response.choices[0].message.content,
            "sentiment": sentiment
        }