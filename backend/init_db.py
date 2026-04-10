import mysql.connector
from mysql.connector import Error
import os

def create_connection():
    # Try with the known password first
    passwords = ['', 'root', 'password', '']
    
    for p in passwords:
        try:
            # Try with specific database first
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password=p,
                database='movie_recommendation_db',
                connect_timeout=2
            )
            if connection.is_connected():
                return connection
        except Error:
            try:
                # Try without database next
                connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password=p,
                    connect_timeout=2
                )
                if connection.is_connected():
                    return connection
            except Error:
                continue
    
    print("Error while connecting to MySQL: ALL PASSWORDS FAILED.")
    print("Please ensure MySQL is running and update the password in init_db.py if needed.")
    return None

def init_db():
    connection = create_connection()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    schema_path = os.path.join(os.path.dirname(__file__), '../database/schema.sql')
    if not os.path.exists(schema_path):
        print(f"Schema file not found at {schema_path}")
        return

    # Read schema.sql
    with open(schema_path, 'r') as f:
        schema = f.read()

    # Split schema and execute each statement separately
    # This is more robust than multi=True which depends on library version
    statements = schema.split(';')
    for statement in statements:
        if statement.strip():
            try:
                cursor.execute(statement)
                # Consume result if any
                while cursor.nextset():
                    pass
            except Error as e:
                print(f"Statement failed: {statement[:50]}... Error: {e}")

    print("Database and table created successfully.")
    
    # ─────────────────────────────────────────────────────────────────────────
    # ALL 45 MOVIES — covering every mood/emotion category
    # ─────────────────────────────────────────────────────────────────────────
    movies = [
        # ORIGINAL 15 MOVIES (Enriched Moods)
        (1, 'RRR', 'Action, Drama', 'Telugu, Hindi, Tamil', 'Motivational', 8.8,
         'Two legendary revolutionaries fight for their country in 1920s.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/d/d7/RRR_Poster.jpg', 2022,
         'N.T.R. Jr., Ram Charan'),
        (2, 'Baahubali: The Beginning', 'Action, Drama, Fantasy', 'Telugu, Hindi, Tamil', 'Motivational', 8.0,
         'In ancient India, an adventurous and daring man becomes involved in a decades-old feud.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/5/5f/Baahubali_The_Beginning_poster.jpg', 2015,
         'Prabhas, Rana Daggubati'),
        (3, 'Baahubali 2: The Conclusion', 'Action, Drama, Fantasy', 'Telugu, Hindi, Tamil', 'Happy', 8.2,
         'Amarendra Baahubali claims the throne.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/f/f9/Baahubali_the_Conclusion.jpg', 2017,
         'Prabhas, Rana Daggubati'),
        (4, 'KGF: Chapter 1', 'Action, Crime, Drama', 'Kannada, Hindi, Telugu', 'Action', 8.2,
         'In the 1970s, a gangster goes undercover as a slave.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/c/c0/K.G.F_Chapter_1_poster.jpg', 2018,
         'Yash, Srinidhi Shetty'),
        (5, 'KGF: Chapter 2', 'Action, Crime, Drama', 'Kannada, Hindi, Telugu', 'Action', 8.3,
         "In the blood-soaked Kolar Gold Fields, Rocky's name strikes fear.",
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/d/d0/K.G.F_Chapter_2.jpg', 2022,
         'Yash, Sanjay Dutt'),
        (6, 'Dangal', 'Action, Biography, Drama', 'Hindi', 'Motivational', 8.3,
         'Former wrestler Mahavir Singh Phogat and his daughters struggle towards glory.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/9/99/Dangal_Poster.jpg', 2016,
         'Aamir Khan, Sakshi Tanwar'),
        (7, '3 Idiots', 'Comedy, Drama', 'Hindi', 'Happy', 8.4,
         'Two friends are searching for their long lost companion.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/d/df/3_idiots_poster.jpg', 2009,
         'Aamir Khan, Madhavan'),
        (8, 'Drishyam', 'Crime, Drama, Thriller', 'Malayalam, Hindi', 'Sad', 8.2,
         'Desperate measures are taken by a man who tries to save his family.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/1/1b/Drishyam_poster.jpg', 2013,
         'Mohanlal, Meena'),
        (9, 'Vikram', 'Action, Thriller', 'Tamil, Hindi', 'Action', 8.3,
         'A special investigator discovers a case of serial killings.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/8/8b/Vikram_2022_poster.jpg', 2022,
         'Kamal Haasan, Vijay Sethupathi'),
        (10, 'Pushpa: The Rise', 'Action, Crime, Drama', 'Telugu, Hindi', 'Angry', 7.6,
         'A laborer rises through the ranks of a red sandal smuggling syndicate.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/1/11/Pushpa_The_Rise_Part_1.jpg', 2021,
         'Allu Arjun, Fahadh Faasil'),
        (11, 'Kantara', 'Action, Adventure, Drama', 'Kannada, Hindi', 'Thrilled', 8.3,
         'When greed paves the way, a young tribal seeks justice.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/8/84/Kantara_poster.jpeg', 2022,
         'Rishab Shetty, Kishore'),
        (12, 'Jawan', 'Action, Thriller', 'Hindi', 'Motivational', 7.0,
         'A high-octane action thriller outlines an emotional journey.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/3/39/Jawan_film_poster.jpg', 2023,
         'Shah Rukh Khan, Nayanthara'),
        (13, 'Pathaan', 'Action, Thriller', 'Hindi', 'Happy', 5.9,
         'An Indian spy takes on the leader of a group of mercenaries.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/c/c3/Pathaan_film_poster.jpg', 2023,
         'Shah Rukh Khan, John Abraham'),
        (14, 'Sita Ramam', 'Action, Drama, Mystery, Romance', 'Telugu, Hindi', 'Romantic', 8.5,
         "An orphan soldier's life changes after he gets a letter from a girl.",
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/e/e6/Sita_Ramam.jpg', 2022,
         'Dulquer Salmaan, Mrunal Thakur'),
        (15, 'Jersey', 'Drama, Sport', 'Telugu, Hindi', 'Sad', 8.5,
         'A failed cricketer decides to revive his cricketing career.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/a/a2/Jersey_2019_poster.jpg', 2019,
         'Nani, Shraddha Srinath'),

        # HAPPY MOOD MOVIES
        (16, 'Munna Bhai M.B.B.S.', 'Comedy, Drama', 'Hindi', 'Happy', 8.1,
         'A gangster sets out to fulfill his father\'s dream by becoming a doctor.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/8/8c/Munna_Bhai_MBBS.jpg', 2003,
         'Sanjay Dutt, Arshad Warsi'),
        (17, 'Andhadhun', 'Crime, Mystery, Thriller', 'Hindi', 'Surprised', 8.3,
         'A series of unexpected events unfold after a blind pianist witnesses a murder.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/0/09/AndhaDhun_poster.jpg', 2018,
         'Ayushmann Khurrana, Tabu'),
        (18, 'Golmaal: Fun Unlimited', 'Comedy', 'Hindi', 'Happy', 7.4,
         'Four friends live in an old woman\'s house by pretending one of them is blind.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/1/1d/Golmaal_fun_unlimited.jpg', 2006,
         'Ajay Devgn, Arshad Warsi'),
        (19, 'Hera Pheri', 'Comedy', 'Hindi', 'Happy', 8.2,
         'Three unemployed men accidentally get caught in a ransom call.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/5/52/Hera_Pheri_poster.jpg', 2000,
         'Akshay Kumar, Sunil Shetty, Paresh Rawal'),
        (20, 'PK', 'Comedy, Drama', 'Hindi', 'Happy', 8.1,
         'An alien lands on Earth and questions the concept of God and religion.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/b/bd/PK_poster.jpg', 2014,
         'Aamir Khan, Anushka Sharma'),

        # SAD MOOD MOVIES
        (21, 'Ae Dil Hai Mushkil', 'Drama, Romance', 'Hindi', 'Sad', 6.7,
         'A heartbroken man navigates one-sided love in this emotional journey.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/8/87/Ae_Dil_Hai_Mushkil.jpg', 2016,
         'Ranbir Kapoor, Anushka Sharma'),
        (22, 'Taare Zameen Par', 'Drama', 'Hindi', 'Sad', 8.4,
         'An 8-year-old dyslexic child is befriended by an art teacher who recognizes his talents.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/2/27/Taare_Zameen_Par.jpg', 2007,
         'Aamir Khan, Darsheel Safary'),
        (23, 'Udaan', 'Drama', 'Hindi', 'Sad', 8.1,
         'A teenager returns home after being expelled from boarding school.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/9/9b/Udaan_2010_poster.jpg', 2010,
         'Rajat Barmecha, Ronit Roy'),
        (24, 'Masaan', 'Drama, Romance', 'Hindi', 'Sad', 8.1,
         'Four lost souls seek meaning after tragedy strikes them.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/e/e5/Masaan_film_poster.jpg', 2015,
         'Richa Chadha, Vicky Kaushal'),
        (25, 'Kapoor and Sons', 'Drama', 'Hindi', 'Sad', 7.7,
         'Two brothers come home to their ailing grandfather and old family tensions resurface.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/0/06/Kapoor_and_Sons_poster.jpg', 2016,
         'Sidharth Malhotra, Fawad Khan'),

        # MOTIVATIONAL MOOD MOVIES
        (26, 'Bhaag Milkha Bhaag', 'Biography, Drama, Sport', 'Hindi', 'Motivational', 8.0,
         'The story of Milkha Singh, the legendary Indian sprinter.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/e/ef/Bhaag_Milkha_Bhaag.jpg', 2013,
         'Farhan Akhtar, Sonam Kapoor'),
        (27, 'MS Dhoni: The Untold Story', 'Biography, Drama, Sport', 'Hindi', 'Motivational', 8.0,
         'The journey of Mahendra Singh Dhoni from a small town to becoming World Cup captain.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/1/17/MS_Dhoni_-_The_Untold_Story.jpg', 2016,
         'Sushant Singh Rajput, Kiara Advani'),
        (28, 'Super 30', 'Biography, Drama', 'Hindi', 'Motivational', 7.2,
         'Mathematician Anand Kumar trains 30 underprivileged students for IIT entrance.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/2/21/Super_30_film_poster.jpg', 2019,
         'Hrithik Roshan, Mrunal Thakur'),
        (29, 'Chak De India', 'Drama, Sport', 'Hindi', 'Motivational', 8.2,
         'A disgraced hockey player coaches the Indian women\'s national team.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/f/f8/Chak_De_India_poster.jpg', 2007,
         'Shah Rukh Khan, Vidya Malvade'),
        (30, '83', 'Biography, Drama, Sport', 'Hindi', 'Motivational', 7.8,
         'The story of India\'s historic 1983 Cricket World Cup victory.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/a/a9/83_film_poster.jpg', 2021,
         'Ranveer Singh, Deepika Padukone'),

        # ACTION / ANGRY MOOD MOVIES
        (31, 'War', 'Action, Thriller', 'Hindi', 'Angry', 5.1,
         'An Indian soldier is tasked to eliminate his former mentor.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/7/7d/War_2019_film_poster.jpg', 2019,
         'Hrithik Roshan, Tiger Shroff'),
        (32, 'Simmba', 'Action, Comedy, Crime', 'Hindi', 'Angry', 6.2,
         'A corrupt police officer becomes a crusader after a personal tragedy.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/f/f4/Simmba_poster.jpg', 2018,
         'Ranveer Singh, Sara Ali Khan'),
        (33, 'Uri: The Surgical Strike', 'Action, Thriller', 'Hindi', 'Motivational', 8.2,
         'Indian army carries out a surgical strike against militants.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/1/18/Uri_The_Surgical_Strike_poster.jpg', 2019,
         'Vicky Kaushal, Paresh Rawal'),
        (34, 'Sye Raa Narasimha Reddy', 'Action, Biography, Drama', 'Telugu, Hindi', 'Motivational', 6.5,
         'The life of freedom fighter Uyyalawada Narasimha Reddy.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/8/86/Sye_Raa_Narasimha_Reddy.jpg', 2019,
         'Chiranjeevi, Amitabh Bachchan'),
        (35, 'Saaho', 'Action, Thriller', 'Telugu, Hindi', 'Angry', 5.3,
         'A cop investigates a theft case and gets entangled in a bigger conspiracy.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/c/c4/Saaho_poster.jpg', 2019,
         'Prabhas, Shraddha Kapoor'),

        # ROMANTIC MOOD MOVIES
        (36, 'Dilwale Dulhania Le Jayenge', 'Drama, Romance', 'Hindi', 'Romantic', 8.1,
         'A young man and woman fall in love on a trip across Europe.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/9/9d/Dilwale_Dulhania_Le_Jayenge_poster.jpg', 1995,
         'Shah Rukh Khan, Kajol'),
        (37, 'Kabir Singh', 'Drama, Romance', 'Hindi', 'Romantic', 7.1,
         'A brilliant but short-tempered surgeon falls into self-destruction after his love marries another.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/6/6f/Kabir_Singh_poster.jpg', 2019,
         'Shahid Kapoor, Kiara Advani'),
        (38, 'Jab We Met', 'Comedy, Romance', 'Hindi', 'Romantic', 7.9,
         'A depressed businessman meets a bubbly girl on a train.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/8/8e/Jab_We_Met.jpg', 2007,
         'Shahid Kapoor, Kareena Kapoor'),
        (39, 'Kal Ho Naa Ho', 'Comedy, Drama, Romance', 'Hindi', 'Romantic', 8.0,
         'A terminally ill man changes the lives of his neighbors.',
         'Netflix', 'https://upload.wikimedia.org/wikipedia/en/5/5c/Kal_Ho_Naa_Ho_poster.jpg', 2003,
         'Shah Rukh Khan, Preity Zinta'),
        (40, 'Brahmastra', 'Action, Fantasy, Romance', 'Hindi', 'Romantic', 5.6,
         'A young man discovers his unique superpower and fights dark forces.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/8/89/Brahmastra_Part_One.jpg', 2022,
         'Ranbir Kapoor, Alia Bhatt'),

        # FEARFUL / SURPRISED MOOD MOVIES
        (41, 'Kahaani', 'Crime, Mystery, Thriller', 'Hindi', 'Fearful', 8.1,
         'A pregnant woman searches for her missing husband in Kolkata.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/3/30/Kahaani_poster.jpg', 2012,
         'Vidya Balan, Parambrata Chatterjee'),
        (42, 'Talaash', 'Crime, Drama, Mystery', 'Hindi', 'Fearful', 7.5,
         'A detective investigates a celebrity\'s death and gets drawn into a dark mystery.',
         'Hotstar', 'https://upload.wikimedia.org/wikipedia/en/1/12/Talaash_film_poster.jpg', 2012,
         'Aamir Khan, Rani Mukerji'),
        (43, 'Ratsasan', 'Crime, Thriller', 'Tamil, Hindi', 'Fearful', 8.4,
         'An aspiring filmmaker becomes a cop and hunts a serial killer.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/3/3e/Ratsasan_poster.jpg', 2018,
         'Vishnu Vishal, Amala Paul'),
        (44, 'Tumbbad', 'Fantasy, Horror, Thriller', 'Hindi', 'Fearful', 8.2,
         'A mythological story about a God who was cast out of heaven for wanting all the wealth.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/8/8b/Tumbbad_poster.jpg', 2018,
         'Sohum Shah, Anita Date'),
        (45, 'Article 15', 'Crime, Drama, Mystery', 'Hindi', 'Neutral', 8.0,
         'A cop investigates the case of two missing girls in rural India.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/2/2b/Article_15_poster.jpg', 2019,
         'Ayushmann Khurrana, Nassar'),
        (46, 'Gully Boy', 'Musical, Drama', 'Hindi', 'Neutral', 7.9,
         'The story of a young Muslim man from the slums of Mumbai who becomes a rapper.',
         'Amazon Prime Video', 'https://upload.wikimedia.org/wikipedia/en/0/07/Gully_Boy_poster.jpg', 2019,
         'Ranveer Singh, Alia Bhatt'),
    ]

    insert_query = """
    INSERT INTO movies (id, title, genre, language, mood, rating, description, ott_platform, poster_url, release_year, cast_members)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
    title=VALUES(title), genre=VALUES(genre), language=VALUES(language), 
    mood=VALUES(mood), rating=VALUES(rating), description=VALUES(description), 
    ott_platform=VALUES(ott_platform), poster_url=VALUES(poster_url),
    release_year=VALUES(release_year), cast_members=VALUES(cast_members)
    """

    cursor.executemany(insert_query, movies)
    connection.commit()
    print(f"Inserted/updated {len(movies)} movies successfully.")

    cursor.close()
    connection.close()

if __name__ == '__main__':
    init_db()
