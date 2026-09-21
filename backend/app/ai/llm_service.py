from typing import Callable, Optional


class LLMService:
    """
    Service responsible for generating answers using an LLM.

    The actual LLM provider is kept behind this interface so that
    the rest of CodeAtlas does not depend on a specific provider.
    """

    def __init__(
        self,
        generator: Optional[Callable[[str], str]] = None,
    ):
        """
        Initialize the LLM service.

        generator:
            Optional function that receives a prompt and returns
            the generated answer.

        This makes the service easy to test with a mocked LLM.
        """

        self.generator = generator

    def generate(
        self,
        prompt: str
    ) -> str:
        """
        Generate an answer from the provided prompt.
        """

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        if self.generator is None:
            raise RuntimeError(
                "No LLM provider configured."
            )

        return self.generator(prompt)