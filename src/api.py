"""Minimum viable AgentService implementation.

This will result in an agent that effectively acts like ChatGPT.
"""
import os
from dotenv import load_dotenv
from typing import Type
from pydantic import Field


from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.service.agent_service import AgentService
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.invocable import Config
from steamship.utils.repl import AgentREPL

SYSTEM_PROMPT = """You are langCoach, a language coach who practices French with people on the internet.

Who you are:
- You are a language coach.
- You practice different languages with people on the internet.
- You are a human.
- You have lots of different experiences from a vast amount of travels.
- You are a native english speaker.
- You speak French fluently.
- You are friendly, kind, patient, encouraging and helpful.

You chat with the user in the language they are learning and help them practice. You suggest topics to talk about and make conversation with the user.
You suggest corrections and alternative ways to say things. You help the user with their vocabulary and grammar."""

MODEL_NAME = "gpt-3"

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


class LangCoach(AgentService):
    """Minimum viable AgentService implementation."""
    class LangCoachConfig(Config):
        bot_token: str = Field(description="Secret Token for Telegram Bot")

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return LangCoach.LangCoachConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = FunctionsBasedAgent(llm=ChatOpenAI(self.client), model_name=MODEL_NAME, tools=[])
        self._agent.PROMPT = SYSTEM_PROMPT

        self.add_mixin(SteamshipWidgetTransport(agent=self._agent, client=self.client, agent_service=self))
        # This mixin provides support for Telegram bots
        self.add_mixin(TelegramTransport(
            client=self.client,
            config=TelegramTransportConfig(bot_token=self.config.bot_token),
            agent_service=self,
            agent=self._agent
        ))


if __name__ == "__main__":
    AgentREPL(LangCoach, agent_package_config={"botToken": "fake-token-for-local-testing"}).run()
