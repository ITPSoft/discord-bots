## DecimAutomation main functionality
# parsing the "cronjob" file
import json
from datetime import datetime as dt

TARGETS = {
        "decimautomation" : "DecimAutomation#4633",
        "decimbot2": 996439005405126787,
        "basedschizo" : 1044650088494010478
    }

INTERVALS = {
    "@minutely" : 60,
    "@five" : 300,
    "@hourly" : 3600,
    "@daily" : 3600 * 24,
    "@weekly" : 3600 * 24 * 7,
    "@yearly" : 3600 * 24 * 365
}

class Automaton:
    def __init__(self) -> None:
        self.jobs: list = []
        pass

    def parse_cronjobs(self, path: str = "./cronjobs") -> None:
        with open(file=path, encoding="utf-8", mode="r") as file:
            for line in file.readlines():
                if line[0] == "#":
                    pass
                elif line[0] == "@":
                    self.jobs.append(line.replace("\n","").split(" "))
        print(f"Job list parsed. Number of jobs: {len(self.jobs)}\nList of jobs:\n{self.print_jobs()}")

    def work_job(self, job) -> str:
        print(f"Processing job: {job[1]}|{job[2]}...")
        f = open("./jobslock.json", encoding="utf-8", mode="r")
        lf = json.load(f)
        f.close()
        lf.update(
                {
                    job[1]:
                     {
                        job[2] : dt.now().timestamp().__int__()
                        }
                })
        f = open("./jobslock.json", encoding="utf-8", mode="w")
        json.dump(lf, f)
        f.close()
        
        return f"{TARGETS[job[1]]};{job[2]}"

    # working on jobs loop
    def precheck_jobs(self):
        results = []
        for job in self.jobs:
            result = self.check_job_done(name=job[2], target=job[1], interval=job[0])
            if result:
                results.append(self.work_job(job))
            else:
                pass
        return results

    # check if job was already done
    def check_job_done(self, name: str = None, target: str = None, interval: str = None) -> bool:
        with open("./jobslock.json", encoding="utf-8", mode="r") as f:
            lf = json.load(f)
            try:
              if lf[target][name] and \
                      dt.now().timestamp().__int__() - lf[target][name] > INTERVALS[interval]:
                  return True
              else:
                  return False
            except Exception as exc:
                print(f"Job {target}|{name} not present or ran for the first time! Running the job...")
                return True


    # prints out jobs
    def print_jobs(self):
        joblist = ""
        for job in self.jobs:
            joblist += f"Job {self.jobs.index(job)}: {job[0]} {job[1]} {job[2]}\n"
        return joblist

if __name__ == "__main__":
    pass