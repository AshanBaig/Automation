from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from faker import Faker
import time
import random

# Setup Faker for desi-style emails
fake = Faker()

def generate_desi_email():
    if random.randint(0,1):
        first_names = ["Ahmed", "Ayesha", "Usman", "Sana", "Bilal", "Zain", "Fatima", "Imran", "Hira", "Faisal", "Rabia", "Hassan", "Mahnoor", "Saad", "Laiba", "Danish", "Mehwish", "Talha", "Nida", "Waleed"]
        last_names = ["Khan", "Siddiqui", "Qureshi", "Malik", "Hussain", "Abbas", "Iqbal", "Sheikh", "Javed", "Raza", "Anwar", "Ali", "Shah", "Ahmed", "Khan", "Farooq", "Rafiq", "Waheed", "Bukhari", "Mirza"]
    else:
        first_names = ["Rahul", "Priya", "Amit", "Neha", "Arjun", "Anjali", "Ravi", "Pooja", "Vikram", "Sonal", "Karan", "Deepa", "Suresh", "Meena", "Manish", "Kavita", "Rohit", "Sneha", "Vikas", "Divya"]
        last_names = ["Sharma", "Verma", "Singh", "Patel", "Reddy", "Iyer", "Chopra", "Nair", "Desai", "Gupta", "Joshi", "Mehra", "Kapoor", "Shukla", "Bansal", "Malhotra", "Agarwal", "Tripathi", "Yadav", "Pandey"]

    first = random.choice(first_names)
    last = random.choice(last_names)
    number = random.randint(10, 9999)
    mark = [".","_",""]
    return f"{first}{random.choice(mark)}{last}{number}@gmail.com"
generate_desi_email()

# Setup Chrome Driver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Uncomment for background running
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Google Form link (replace with your own form URL)
form_url = "https://docs.google.com/forms/d/e/1FAIpQLScZgjPuxS2_LlDz1UTyEe4JAoAgFez2ugEP2r_-sXKJ_jaFAA/viewform"

def fill_form():
    try:
        driver.get(form_url)
        time.sleep(2)

        # 1. Fill Email (First Text Box)
        text_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="email"]')
        if text_inputs:
            email = generate_desi_email()
            text_inputs[0].send_keys(email)
            print(f"✅ Email entered: {email}")
        else:
            print("❌ Email input not found!")

        time.sleep(1)
        # 2. Select checkboxes for each question group (Assuming fixed order)
        all_checkboxes = driver.find_elements(By.XPATH, '//div[@role="radio"]')
        print(f"✅ Total Checkboxes found: {len(all_checkboxes)}")

        gender_choice = random.choice(all_checkboxes[0:2])
        gender_choice.click()
        time.sleep(0.5)
        breathing_choice = random.choice(all_checkboxes[2:6])
        breathing_choice.click()
        time.sleep(0.5)

        skin_choice = random.choice(all_checkboxes[6:10])
        skin_choice.click()
        time.sleep(0.5)
        freq_choice = random.choice(all_checkboxes[10:15])
        freq_choice.click()
        time.sleep(0.5)
        breathe_choice = random.choice(all_checkboxes[15:19])
        breathe_choice.click()
        time.sleep(0.5)

        skin_choice = random.choice(all_checkboxes[20:23])
        skin_choice.click()
        time.sleep(0.5)
        
        skin_choice = random.choice(all_checkboxes[24:26])
        skin_choice.click()
        time.sleep(0.5)
        skin_choice = random.choice(all_checkboxes[26:28])
        skin_choice.click()
        time.sleep(0.5)
        skin_choice = random.choice(all_checkboxes[28:31])
        skin_choice.click()
        time.sleep(0.5)
        skin_choice = random.choice(all_checkboxes[31:34])
        skin_choice.click()
        
        skin_choice = random.choice(all_checkboxes[35:37])
        skin_choice.click()
        time.sleep(0.5)
        skin_choice = random.choice(all_checkboxes[37:40])
        skin_choice.click()
        time.sleep(0.5)
        skin_choice = random.choice(all_checkboxes[41:44])
        skin_choice.click()
        skin_choice = random.choice(all_checkboxes[44:46])
        skin_choice.click()
        time.sleep(0.5)
        skin_choice = random.choice(all_checkboxes[46:49])
        skin_choice.click()
        time.sleep(0.5)
        skin_choice = random.choice(all_checkboxes[49:52])
        skin_choice.click()
        time.sleep(0.5)
        skin_choice = random.choice(all_checkboxes[52:55])
        skin_choice.click()
        skin_choice = random.choice(all_checkboxes[55:57])
        skin_choice.click()
        time.sleep(0.5)
        skin_choice = random.choice(all_checkboxes[57:59])
        skin_choice.click()
        
        
        
        time.sleep(1)
        

        # Submit the form
        submit_button = driver.find_element(By.XPATH, '//span[contains(text(), "Submit")]')
        submit_button.click()
        print(f"✅ Form submitted for: {email}")

    except Exception as e:
        print(f"❌ Error filling form: {e}")

# Fill multiple times
for i in range(400,600):  # Change to 100 for mass submit
    print(f"--- Filling Form #{i+1} ---")
    fill_form()
    time.sleep(random.uniform(1,2))

driver.quit()
