import pywhatkit as kit
import pyautogui
import time

def send_whatsapp_invitation(link, phone_numbers):
    for phone in phone_numbers:
        try:
            # Open WhatsApp for the current phone number
            kit.sendwhatmsg_instantly(phone, f"Join our WhatsApp group using this link: {link}", wait_time=20)
            time.sleep(15)  # Allow time for the chat to load
            
            # Send the message
            pyautogui.hotkey('enter')  # Simulate pressing 'Enter' to send the message
            print(f"Invitation link sent to {phone}")
            time.sleep(5)  # Wait before closing the tab

            # Close the current tab
            pyautogui.hotkey('ctrl', 'w')  # Simulate Ctrl + W to close the tab
            time.sleep(2)  # Wait for the tab to close

        except Exception as e:
            error.append(phone)
            print(f"Failed to send message to {phone}: {e}")

# Usage
invitation_link = "https://chat.whatsapp.com/FMAmpHZH3i63Wg2pglIQWf"# Replace with your actual group link

phone_numbers_list = []  # Add more numbers as needed
error=[]
def fetch_number():
    with open("usernum.txt") as file:
        count=1
        for i in file:
            count+=1
            i=i.replace(" ",'').replace("-","").replace("\n","")
            if len(i)<10:
                error.append(count)
                continue
            if i[0]=="+":
                if i[2]=="4" and len(i)==12:
                    phone_numbers_list.append(i)
                elif i[2]=="2" and len(i)==13:
                    phone_numbers_list.append(i)
                else:
                    error.append(count)
            elif i[0]=="0" and len(i)==11:
                i="+92"+i[1:]
                phone_numbers_list.append(i)
            else:
                error.append(count)
fetch_number()
# print(phone_numbers_list)
send_whatsapp_invitation(invitation_link, phone_numbers_list)
print(error)