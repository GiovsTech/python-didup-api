from didup_api import Client, Argo
import asyncio
from datetime import datetime, timedelta

client = Client("SCHOOL_CODE", "USERNAME", "PASSWORD", "/path/to/config") ## HERE THE CREDENTIALS THE SCHOOL ADMINISTRATION HAS GIVEN TO YOU
argo = Argo(client)

### JUST AN EXAMPLE OF HOW THE LIBRARY WORKS:
### THIS CODE JUST PRINTS THE HOMEWORK THE STUDENT HAS TO DO FOR THE NEXT DAY

async def main():

    await argo.client.login()
    my_profilo = await argo.select_user("STUDENT_NAME", "STUDENT_SURNAME") ## STUDENT'S INFORMATION

    dashboard = await argo.get_dashboard()
    #profile_details = await argo.get_details()
    #print(profile_details)
    #print(dashboard)
    all_compiti = {}
    for x in dashboard["dati"]:
        if x["registro"]:

            for t in x["registro"]:
                all_compiti[t["materia"]] = t["compiti"]
    current_date = datetime.now()
    next_date = current_date + timedelta(days=1)
    next_day_date = next_date.date()

    for m in all_compiti.values():
        for n in m:
            if str(next_day_date) == n["dataConsegna"]:
                print(f"{list(all_compiti.keys())[list(all_compiti.values()).index(m)]}: " + f"{n["compito"]}")

asyncio.run(main())





