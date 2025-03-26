import httpx
from datetime import datetime
from app.core.config import get_settings
from app.core.exceptions import MetalabsAPIError

settings = get_settings()

class MetalabsService:
    def __init__(self):
        self.api_key = settings.METALABS_API_KEY
        self.base_url = "https://meta-api.metalabs.work/api/v3"
        self.headers = {"Meta-Api-Key": self.api_key}

    async def get_user_uuid(self, project_name: str, username: str) -> str:
        url = f"{self.base_url}/users/{project_name}/get/uuids"
        params = {"nicks[]": username}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("body", {}).get(username, "UUID не найден")
            raise MetalabsAPIError("Ошибка при получении UUID")

    async def get_user_skin(self, project_name: str, user_uuid: str) -> str:
        return f"{self.base_url}/users/skins/{project_name}/head/{user_uuid}"

    async def get_monthly_playtime(self, project_name: str, server_name: str, user_uuid: str) -> str:
        url = f"{self.base_url}/playtime/{project_name}/{server_name}/list"
        params = {"uuids[]": user_uuid}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if not data.get('error') and 'body' in data and user_uuid in data['body']:
                    online_points = data['body'][user_uuid].get('onlinePoints', {})
                    current_date = datetime.now()
                    year, month = current_date.year, current_date.month

                    total_seconds = sum(
                        time for date, time in online_points.items() 
                        if date.startswith(f"{year}-{month:02d}")
                    )

                    hours, minutes = divmod(total_seconds // 60, 60)
                    return f"{hours}ч {minutes}м"
            return "Нет данных"

    async def get_server_staff(self, project_name: str, server_name: str) -> dict:
        url = f"{self.base_url}/users/{project_name}/{server_name}/staff"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if not data.get('error') and 'body' in data and 'users' in data['body']:
                    users = data['body']['users']
                    staff = {
                        "curators": [],
                        "grandmoderators": [],
                        "stmoderators": [],
                        "moderators": [],
                        "helpers": [],
                        "interns": []
                    }

                    for uuid, group in users.items():
                        if group == 'group.curator':
                            staff["curators"].append(uuid)
                        elif group == 'group.grandmoderator':
                            staff["grandmoderators"].append(uuid)
                        elif group == 'group.stmoderator':
                            staff["stmoderators"].append(uuid)
                        elif group == 'group.moder':
                            staff["moderators"].append(uuid)
                        elif group == 'group.helper':
                            staff["helpers"].append(uuid)
                        elif group == 'group.stajer':
                            staff["interns"].append(uuid)

                    return staff
            return None

    async def get_nicknames_by_uuids(self, uuids: list, project_name: str) -> dict:
        if not uuids:
            return {}
        
        url = f"{self.base_url}/users/{project_name}/get/nicks"
        params = {"uuids[]": uuids}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("body", {})
            return {}

    async def get_staff_activity(self, project_name: str, server_name: str, uuids: list, nicknames: dict) -> list:
        url = f"{self.base_url}/playtime/{project_name}/{server_name}/list"
        params = {"uuids[]": uuids}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                raise MetalabsAPIError("Ошибка при запросе онлайна")

            data = response.json()
            if data.get("error") or "body" not in data:
                raise MetalabsAPIError("Ошибка API")

            online_points = data["body"]
            current_date = datetime.now()
            current_year = str(current_date.year)
            current_month = f"{current_date.month:02d}"

            activity_list = []
            for uuid in uuids:
                user_data = online_points.get(uuid, {})
                total_seconds = sum(
                    time for date, time in user_data.get("onlinePoints", {}).items()
                    if date.startswith(f"{current_year}-{current_month}")
                )

                hours, minutes = divmod(total_seconds // 60, 60)
                time_str = f"{hours}ч {minutes}м"
                total_minutes = hours * 60 + minutes

                activity_list.append({
                    "nickname": nicknames.get(uuid, uuid),
                    "hours": time_str,
                    "total_minutes": total_minutes
                })

            activity_list.sort(key=lambda x: x["total_minutes"], reverse=True)
            return activity_list

    async def get_playtime_period(self, project_name: str, server_name: str, nickname: str, start_date: str, end_date: str) -> dict:
        uuid = await self.get_user_uuid(project_name, nickname)
        if uuid == "UUID не найден":
            return {"error": "Пользователь не найден"}

        url = f"{self.base_url}/playtime/{project_name}/{server_name}/list"
        params = {
            "min": start_date,
            "max": end_date,
            "uuids[]": uuid
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if not data.get('error') and 'body' in data and uuid in data['body']:
                    online_points = data['body'][uuid].get('onlinePoints', {})
                    total_seconds = sum(online_points.values())
                    hours, minutes = divmod(total_seconds // 60, 60)
                    return {"nickname": nickname, "time": f"{hours}ч {minutes}м"}
            return {"error": "Не удалось получить данные"}

    async def replace_uuids_with_nicknames(self, staff: dict, nicknames: dict) -> dict:
        def replace_uuids(uuid_list):
            return [nicknames.get(uuid, uuid) for uuid in uuid_list]

        staff["curators"] = replace_uuids(staff["curators"])
        staff["grandmoderators"] = replace_uuids(staff["grandmoderators"])
        staff["stmoderators"] = replace_uuids(staff["stmoderators"])
        staff["moderators"] = replace_uuids(staff["moderators"])
        staff["helpers"] = replace_uuids(staff["helpers"])
        staff["interns"] = replace_uuids(staff["interns"])
        return staff 