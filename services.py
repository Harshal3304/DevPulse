import httpx 

async def fetch_github_profile(github_handle: str):
    if not github_handle:
        return {"error": "No GitHub handle provided"}

    url = f"https://api.github.com/users/{github_handle}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data.get("name"),
                "public_repos": data.get("public_repos"),
                "followers": data.get("followers"),
                "avatar_url": data.get("avatar_url")
            }
        
        return {"error": "User Not Found"}