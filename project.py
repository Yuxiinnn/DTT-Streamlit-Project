import streamlit as st
import random
import speech_recognition as sr
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to generate a greeting message
def greet_user():
    greetings = [
        "Hello! Thank you for choosing Talk2Order! What would you like to order today?",
        "Welcome to Talk2Order! What would you like to order today?"
    ]
    return random.choice(greetings)

# Function to speak the text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Menu items with prices
menu_items = {
    "Burgers": {
        "Big Mac": 7.00,
        "Cheeseburger": 3.90,
        "McChicken": 3.65,
        "Filet-O-Fish": 4.80,
        "Quarter Pounder with Cheese": 7.00
    },
    "Fries": {
        "Small Fries": 2.85,
        "Medium Fries": 3.95,
        "Large Fries": 4.20
    },
    "Drinks": {
        "Coke": 2.95,
        "Sprite": 2.95,
        "Fanta": 2.95,
        "Iced Milo": 3.80,
    },
    "Sides": {
        "6 pieces Chicken Nuggets": 5.75,
        "20 pieces Chicken Nuggets": 13.70,
        "Banana Pie": 1.85,
        "Apple Pie": 2.10
    },
    "Desserts": {
        "Strawberry Shortcake McFlurry": 4.00,
        "Oreo McFlurry": 3.60,
        "Hot Fudge Sundae": 2.80,
        "Soft Serve Cone": 1.20
    }
}

# Function to recognize speech
def recognize_speech(prompt=""):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if prompt:
            speak(prompt)  # Speak the prompt
            st.write(prompt)  # Display the prompt in Streamlit

        with st.spinner("Listening..."):
            try:
                audio = recognizer.listen(source, timeout=15)
                order = recognizer.recognize_google(audio)  # Use Google Speech Recognition
                return order
            except sr.WaitTimeoutError:
                st.error("Listening timed out. Please try again.")
                return None
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your speech.")
                return None
            except sr.RequestError:
                st.error("Could not request results from the speech recognition service.")
                return None

# Main application
def main():
    st.title("AI Voice Ordering Kiosk")

    # Display a greeting message
    greeting = greet_user()
    st.write(greeting)
    speak(greeting)

    # Display the menu items
    st.header("Menu Items")
    for category, items in menu_items.items():
        st.subheader(category)
        for item, price in items.items():
            st.write(f"{item}: ${price:.2f}")

    # Flag to track if an order has been placed
    order_placed = False

    while not order_placed:  # Loop until an order is placed
        total_cost = 0
        order_details = {
            "Burger": None,
            "Fries": None,
            "Drink": None,
            "Sides": None,
            "Dessert": None
        }

        # Sequentially prompt for each category
        for category in ["Burgers", "Fries", "Drinks", "Sides", "Desserts"]:
            found = False
            prompt_message = f"Please say your {category.lower()}."
            st.header(prompt_message)
            speak(prompt_message)

            while not found:  # Keep asking until a valid item is found
                order = recognize_speech()
                if order:
                    order_lower = order.lower()

                    # Check if the user said "none"
                    if "none" in order_lower:
                        order_details[category[:-1]] = "None"
                        found = True
                        st.write(f"No {category.lower()} added to your order.")
                        break  # Exit the loop if "none" is detected

                    # Enhanced matching for sides to improve detection
                    if category == "Sides":
                        side_variants = {
                            "6 pieces Chicken Nuggets": ["six pieces of chicken nuggets", "six pieces chicken nuggets", "6 pieces of chicken nuggets", "6 pieces chicken nuggets"],
                            "20 pieces Chicken Nuggets": ["twenty pieces of chicken nuggets", "twenty pieces chicken nuggets", "20 pieces of chicken nuggets", "20 pieces chicken nuggets"],
                            "Banana Pie": ["banana pie"],
                            "Apple Pie": ["apple pie"]
                        }
                        for item, variants in side_variants.items():
                            for variant in variants:
                                if variant in order_lower or order_lower in variant:
                                    order_details[category] = item  # Remove the last character for key
                                    total_cost += menu_items[category][item]
                                    found = True
                                    st.write(f"Found {item} in order!")
                                    break  # Exit loop once an item is found
                        if found:
                            break  # Exit outer loop if item found

                    # Enhanced matching for fries to improve detection
                    elif category == "Fries":
                        for item in menu_items[category].keys():
                            if item.lower() in order_lower or order_lower in item.lower():
                                order_details["Fries"] = item  # Remove the last character for key
                                total_cost += menu_items[category][item]
                                found = True
                                st.write(f"Found {item} in order!")
                                break  # Exit loop once an item is found

                    else:
                        for item, price in menu_items[category].items():
                            if item.lower() in order_lower or order_lower in item.lower():
                                order_details[category[:-1]] = item  # Remove the last character for key
                                total_cost += price
                                found = True
                                st.write(f"Found {item} in order!")
                                break  # Exit loop once an item is found

                if not found:
                    st.warning(f"No valid {category.lower()} found. Please repeat your {category.lower()}.")
                    speak(f"Please say your {category.lower()}.")

        # Prepare confirmation message
        confirmation_message = "Your order has been placed:\n"
        confirmation_message += f"\nBurger: {order_details['Burger'] if order_details['Burger'] else 'None'}\n"
        confirmation_message += f"\nFries: {order_details['Fries'] if order_details['Fries'] else 'None'}\n"
        confirmation_message += f"\nDrink: {order_details['Drink'] if order_details['Drink'] else 'None'}\n"
        confirmation_message += f"\nSides: {order_details['Sides'] if order_details['Sides'] else 'None'}\n"
        confirmation_message += f"\nDessert: {order_details['Dessert'] if order_details['Dessert'] else 'None'}\n"
        confirmation_message += f"\nTotal Cost: ${total_cost:.2f}"

        st.success(confirmation_message)
        speak(confirmation_message)

        order_placed = True  # Set flag to indicate order has been placed

        # Payment method selection using voice
        payment_prompt = "Please say your payment method: Credit Card, Debit Card, or Cash."
        st.write(payment_prompt)
        speak(payment_prompt)

        payment_method = recognize_speech()

        while True:
            if payment_method:
                payment_method = payment_method.lower()
                valid_payments = ["credit card", "debit card", "cash"]

                if payment_method in valid_payments:
                    if payment_method == "cash":
                        payment_confirmation = "Please proceed to the counter to pay by cash."
                    else:
                        payment_confirmation = f"You have chosen to pay by {payment_method.capitalize()}.\n \nPlease tap your card on the payment terminal."

                    st.success(payment_confirmation)
                    speak(payment_confirmation)

                    # Thank You message
                    thank_you_message = "Your Order Number: 6940\n \nThank you for your order!\n \nHave a great day and hope to see you again!"
                    st.success(thank_you_message)
                    speak(thank_you_message)
                    break
                else:
                    st.warning("Invalid payment method. Please repeat your payment method.")
                    speak("Invalid payment method. Please repeat your payment method.")
            else:
                st.warning("No valid input received. Please repeat your payment method.")
                speak("Please repeat your payment method.")

            payment_method = recognize_speech()


if __name__ == "__main__":
    main()