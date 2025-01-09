from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Literal, Any
import signal
import os


class Tasker():
    """
        A slight task threading pools oject to process tasks.

        Parameters:
            task_mode (Literal['map','single']): to run the task mode, 
                                                `map`: use the `map` func of the theading pool to distribute tasks.
                                                `single`: use the `submit` func to distribute the task one by one into the theading pool.
            cus_task (Callable | None = None): a function of the task details.
            task_params_list (list[Any] = []): a list of parameters of the function `cus_task` above. 
            max_threading (int): The maximum number of threads in the threading pool. Default is 3.
            cached_data (bool): weather cache the parsed datas, defalt is False.
            cached_result (bool): wheather need save the task executed result into the cache, default is False, if you set True, you can get the reault from the property `task_result_dict`.
            stop_when_task_failed (bool) : wheather need stop when you failed to get request from a Url,default is True

    """

    def __init__(self,
                 task_mode: Literal['map', 'single'],
                 cus_task: Callable | None = None,
                 task_params_list: list[Any] = [],
                 max_threading: int = 3,
                 cached_result: bool = False,
                 stop_when_task_failed: bool = True
                 ) -> None:
        self.task_mode: Literal['map', 'single'] = task_mode
        self.task_max_threading = max_threading
        self.task_job = cus_task
        self.task_params_list = task_params_list
        self.is_running = False
        self.task_result_dict = {}
        self.cached_result = cached_result
        self.taker_executer = None
        self.futures = [],
        self.stop_when_task_failed = stop_when_task_failed

    def _handle_interrupt(self, signum, frame):  # detect the control + c
        print("Interrupt received, shutting down tasks !!!")
        self.terminal_task()

    def terminal_task(self):
        """
            a func to terminal all tasks and exit current program
        """
        if self.taker_executer:
            if self.task_mode == 'map':
                self.taker_executer.shutdown(wait=False)
            elif self.task_mode == 'sigle':
                for f in self.futures:  # cancel all tasks, even it is running
                    if not f.done():
                        f.cancel()
            # sys.exit(0)  # Exit the program
            # os.kill(os.getpid(), 9)  # force exit program
        print('task canceled, existed the program !!!')
        os._exit(1)  # force exit program

    def start_task(self) -> dict[int,Any] | dict:
        """
            a func to start all tasks 
        """
        # Registering signal handler for Ctrl + C (SIGINT)
        signal.signal(signal.SIGINT, self._handle_interrupt)
        print(f'start to run all tasks !!!')
        self.task_result_dict = {}
        self.is_running = True
        try:
            if self.task_job is None:
                print('no tasks need to run !!!')
                self.is_running = False
                return self.task_result_dict
            with ThreadPoolExecutor(max_workers=self.task_max_threading) as executor:
                self.taker_executer = executor
                if self.task_mode == 'map':  # not recommend, as the task can't be terminated forcely when it started
                    results = executor.map(
                        self.task_job, self.task_params_list)
                    for i, result in enumerate(results):
                        if self.cached_result:
                            self.task_result_dict[self.task_params_list[i]] = result
                        if not result:
                            print(
                                f"warning: when running task {i} with params({self.task_params_list[i]}), we get the None result ! ")
                            if self.stop_when_task_failed:
                                print(
                                    f"warning: failed to run the task {i} with params({self.task_params_list[i]}), it's going to cancel not start jobs ")
                                self.terminal_task()
                                break
                elif self.task_mode == 'single':
                    self.futures = [executor.submit(self.task_job, params)
                                    for params in self.task_params_list]
                    for i, future in enumerate(as_completed(self.futures)):
                        result = future.result()  # jump out when there were an error
                        if self.cached_result:
                            self.task_result_dict[self.task_params_list[i]] = result
                        if not result:
                            print(
                                f"warning: when running task {i} with params({self.task_params_list[i]}), we get the None result ! ")
                            if self.stop_when_task_failed:
                                print(
                                    f"failed to run the task {i} with params({self.task_params_list[i]}), it'going to cancel all running jobs !!!")
                                self.terminal_task()
                                break
                else:
                    print(f'invalid task_mode: {self.task_mode}')
                    executor.shutdown(wait=False)
        except Exception as err:
            print(f'error when running the task jobs, error: {err}.')
        finally:
            self.is_running = False
            print(f'finished all running task !!!')
            return self.task_result_dict
