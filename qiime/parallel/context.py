from IPython.parallel import Client

from qiime.util import load_qiime_config
from qiime.parallel.util import system_call


qiime_config = load_qiime_config()


class ComputeError(Exception):
    pass


class Context(object):
    """Parallel context

    Methods
    -------
    submit_async
    submit_sync
    sync

    """
    def __init__(self, profile):
        try:
            self._client = Client(profile=profile)
        except IOError:
            raise ComputeError("It looks like the profile %s does not exist "
                               "or the cluster is not actually running."
                               % profile)

        self._stage_imports(self._client)
        self._lview = self._client.load_balanced_view()

    def _stage_imports(self, cluster):
        with cluster[:].sync_imports(quiet=True):
            from qiime.parallel.util import system_call

    def sync(self, data):
        """Sync data to engines

        Parameters
        ----------
        data : dict
            dict of objects and to sync

        """
        self._client[:].update(data)

    def submit_async(self, cmd, *args, **kwargs):
        """Submit an async command to execute

        Parameters
        ----------
        cmd : {function, str}
            A function to execute or a system call to execute
        args : list
            Arguments to pass to a function (if cmd is function)
        kwargs : dict
            Keyword arguments to pass to a function (if cmd is function)

        Returns
        -------
        IPython.parallel.client.asyncresult.AsyncResult

        """
        if isinstance(cmd, str):
            task = self._lview.apply_async(system_call, cmd)
        else:
            task = self._lview.apply_async(cmd, *args, **kwargs)

        return task

    def submit_sync(self, cmd, *args, **kwargs):
        """Submit an sync command to execute

        Parameters
        ----------
        cmd : {function, str}
            A function to execute or a system call to execute
        args : list
            Arguments to pass to a function (if cmd is function)
        kwargs : dict
            Keyword arguments to pass to a function (if cmd is function)

        Returns
        -------
        Dependent on cmd

        """
        if isinstance(cmd, str):
            result = self._lview.apply_sync(system_call, cmd)
        else:
            result = self._lview.apply_sync(cmd, *args, **kwargs)

        return result


# likely want this in qiime.parallel.__init__
context = Context(qiime_config['profile'])
