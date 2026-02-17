import json
from typing import AsyncIterator

import httpx


class LLMClient:
    def __init__(
            self,
            http_client: httpx.AsyncClient,
            llm_url: str,
    ):
        self.http_client = http_client
        self.llm_url = llm_url

    async def generate_response(
            self,
            messages: list[dict],
            stream: bool = False,
            temperature: float = 0.7,
            model: str = "local",
    ) -> str | AsyncIterator[str]:
        payload = {
            "model": model,
            "stream": stream,
            "messages": messages,
            "temperature": temperature,
        }

        if stream:
            return self._stream_response(payload)
        else:
            return await self._simple_response(payload)

    async def _stream_response(
            self,
            payload: dict,
    ) -> AsyncIterator[str]:
        async with self.http_client.stream("POST", self.llm_url, json=payload) as response:
            async for line in response.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                if line.endswith("[DONE]"):
                    break

                data = line.removeprefix("data: ").strip()
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta
                except Exception:
                    continue

    async def _simple_response(
            self,
            payload: dict,
    ) -> str:
        response = await self.http_client.post(self.llm_url, json=payload, timeout=500)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def generate_topic_title(
            self,
            text: str,
    ) -> str | None:
        messages = [
            {
                "role": "system",
                "content": (
                    "Задача: придумай краткий заголовок темы по сообщению пользователя.\n"
                    "Требования к заголовку:\n"
                    "- Язык: русский\n"
                    "- Длина: до 128 символов\n"
                    "- 1 строка, без кавычек и без точки в конце\n"
                    "- Отражает суть запроса (что пользователь хочет сделать/узнать/исправить)\n"
                    "- Перефразируй: не копируй и не повторяй текст пользователя дословно, избегай одинаковых формулировок\n"
                    "- Без вводных слов типа «Пользователь спрашивает…»\n"
                    "- Без лишних деталей, имён, ссылок, дат и чисел, если они не критичны для смысла\n"
                    "Если запрос неоднозначный или слишком общий — дай нейтральный, но конкретный заголовок."
                ),
            },
            {"role": "user", "content": text},
        ]

        try:
            response = await self.generate_response(
                model="local",
                messages=messages,
                stream=False,
                temperature=0.2,
            )
            if isinstance(response, str):
                title = response.strip()
                return title[:128] if title else None
            return None
        except Exception as ex:
            # Тут можно что-нибудь залогировать
            return None
