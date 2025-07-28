import yaml
from openai import OpenAI

class Chatbot:
    def __init__(self):
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
        
        self.client = OpenAI(
            api_key=config.get("LLAMA_API_KEY"),
            base_url="https://api.llama.com/compat/v1/",
        )
        self.chat_history = []

    def run(self):
        print("Welcome to the Rubik Pi Chatbot!")
        print("Type 'exit' to quit the chatbot.")
        
        while True:
            user_input = input("You: ")
            print("")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            
            # Add user message to chat history
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Keep only the most recent 20 messages
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]
            
            response = self.client.chat.completions.create(
                model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=self.chat_history,
                max_completion_tokens=1024
            )
            
            # Get the response content
            assistant_response = response.choices[0].message.content
            print("Llama:", assistant_response)
            print("")
            
            # Add assistant response to chat history
            self.chat_history.append({"role": "assistant", "content": assistant_response})
            
            # Keep only the most recent 20 messages after adding assistant response
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]

if __name__ == "__main__":
    chatbot = Chatbot()
    chatbot.run()