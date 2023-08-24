import docker


class DockerRunner():
    
    def __init__(self):

        self.client = docker.from_env()

        return
    
    def containerRun(self, dockerImage, containerName, scriptPath, containerWorkdir):
        
        container = self.containers.run(
            image = dockerImage,
            name = containerName,
            working_dir = containerWorkdir,
            command = ['python', scriptPath],
            volumes = {'./': {'bind': f'{containerWorkdir}', 'mode': 'rw'}, '/dev/video0': {'bind': '/dev/video0', 'mode': 'rw'}},
            detach = True
        )

        # 컨테이너 내 프로세스가 종료되길 기다린다.
        exit_code = container.wait()['StatusCode']

        # 컨테이너 내 프로세스가 종료되었으니 컨테이너를 삭제한다.
        container.remove()

        # 프로세스가 정상 종료되었으면 well, 아니면 something wrong 출력
        if exit_code == 0:
            print(f"{dockerImage}'s {scriptPath} process performed well")
        else:
            print(f"{dockerImage}'s {scriptPath} process something wrong")

        return 
    

class DockerImageSaver():
    
    def __init__(self):

        return
    
    def saveDockerImage():

        return