import httpx
from config import settings

async def send_to_bitrix(user_name: str, user_phone: str, user_email: str, animal_id: int, message: str):
    
    webhook_url = settings.bitrix24_webhook_url
    if not webhook_url:
        print("Ошибка: BITRIX24_WEBHOOK_URL не настроен в .env")
        return
    
    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Создаём контакт
        resp = await client.post(
            f"{webhook_url}crm.contact.add",
            json={"fields": {
                "NAME": user_name,
                "PHONE": [{"VALUE": user_phone, "VALUE_TYPE": "MOBILE"}],
                "EMAIL": [{"VALUE": user_email, "VALUE_TYPE": "WORK"}]
            }}
        )
        result = resp.json()
        if "result" not in result:
            print(f"Ошибка контакта: {result}")
            return
        contact_id = result["result"]
        print(f"Контакт создан: {contact_id}")
        
        # 2. Создаём сделку с кастомными полями
        deal_title = f"Заявка на усыновление от {user_name}"
        resp = await client.post(
            f"{webhook_url}crm.deal.add",
            json={
                "fields": {
                    "TITLE": deal_title,
                    "UF_CRM_1777120185371": animal_id,
                    "UF_CRM_1777120413688": message,
                    "UF_CRM_1777120390258": "48",
                    "COMMENTS": f"ID животного: {animal_id}\nСообщение: {message}"
                }
            }
        )
        result = resp.json()
        if "result" not in result:
            print(f"Ошибка сделки: {result}")
            return
        deal_id = result["result"]
        print(f"Сделка создана: {deal_id}")
        
        # 3. Связываем контакт со сделкой
        await client.post(
            f"{webhook_url}crm.deal.contact.add",
            json={"id": deal_id, "fields": {"CONTACT_ID": contact_id}}
        )
        
        print(f"Отправлено: контакт {contact_id}, сделка {deal_id}")