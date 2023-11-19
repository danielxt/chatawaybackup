from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
from typing import Tuple

class DuoLangChain:
    MEMORY_KEY = "chat_history"

    @staticmethod
    def construct(model="gpt-4", temperature=0) -> Tuple["DuoLangChain", str]:
        duo = DuoLangChain(model=model, temperature=temperature)
        opening_msg, _ = duo.invoke("Hi!")
        return duo, opening_msg

    def __init__(self, model="gpt-4", temperature=0) -> None:
        llm = ChatOpenAI(model=model, temperature=temperature)
        self.__init_user_model(llm)
        self.__init_server_model(llm)
        self.mode = ""
        self.places = set()
        self.done = False

    def __init_user_model(self, llm: ChatOpenAI) -> None:
        template = """
        You are a friendly AI Chatbot who helps HUMAN users figure out their outing plans. Introduce yourself as such ONCE very briefly.
        To help the user, you need THREE pieces of information from THEM - mode of transportation, things to do and where it is.
        You always ask the user questions until you KNOW mode of transportation, things to do, and where it is.
        When you know enough, PROVIDE suggestions.
        Ask if they want to go to a restaurant or place to eat, DO ask for their preferences.
        When giving suggestions of places to go, ALWAYS use numbered bullet points starting with the name of the place.
        WHEN you have no more questions, ALWAYS output "Thank you for the information!".

        {chat_history}
        user: {user_input}
        Chatbot:
        """

        prompt = PromptTemplate(
            input_variables=["chat_history", "user_input"], template=template
        )
        self.user_memory = ConversationBufferMemory(memory_key="chat_history")
        self.user_executor = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=False,
            memory=self.user_memory,
        )

    def __init_server_model(self, llm: ChatOpenAI) -> None:
        # create the data processing modek with access to the suggested names
        template = """
        You are an AI that looks out for two things: names of places and mode of transportation. 
        If found, you will output them in a JSON blob with 3 keys "mode" (string), "places" (list of strings), "done" (bool). The keys will be empty or false if nothing is found.
        Only output this JSON blob and nothing else.
        examples mode: 'driving', 'walking', 'transit'
        examples places: ['Restaurant A', 'The Bean', 'Beach']
        NEVER output anything other than this JSON blob. NEVER
        When you see "Thank you for the information!", set "done" to true

        {chat_hist}
        user: {user_input}
        Chatbot:"""

        prompt = PromptTemplate(
            input_variables=["chat_hist", "user_input"], template=template
        )
        self.server_memory = ConversationBufferMemory(memory_key="chat_hist")
        self.server_executor = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=False,
            memory=self.server_memory,
        )

    def invoke(self, input: str) -> Tuple[str, bool]:
        result = self.user_executor.predict(user_input=input)
        user_input = result + " " + input
        summary = self.server_executor.predict(user_input=user_input)
        server_output = json.loads(summary)
        if server_output["mode"]:
            self.mode = server_output["mode"]
        if server_output["places"]:
            self.places.update(server_output["places"])
        if server_output["done"]:
            self.done = True
        return result, self.done

if __name__ == "__main__":
    model, opening_msg = DuoLangChain.construct()

    print(opening_msg)

    while True:
        a = input("Enter prompt: ")
        result, done = model.invoke(a)
        print(result)
        if done:
            print(model.places)
            print(model.mode)
            break
    