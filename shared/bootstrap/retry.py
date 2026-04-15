from tenacity import retry, stop_after_attempt, wait_exponential

from bootstrap.utils import str_exception


def _before_sleep_factory(logger):
    def log_before_sleep(retry_state):
        attempt_number = retry_state.attempt_number
        last_exception = retry_state.outcome.exception()
        entry_point = retry_state.fn.__name__
        logger.info(f'Retry: {attempt_number=}, {entry_point=}, {last_exception=}')
    return log_before_sleep


def _after_retry_factory(logger):
    def log_after_retry(retry_state):
        attempt_number = retry_state.attempt_number
        is_last_exception = (
            retry_state.retry_object.stop.max_attempt_number == attempt_number
        )
        if is_last_exception and retry_state.outcome.failed:
            last_exception = (
                retry_state.outcome.exception() if retry_state.outcome else None
            )
            exc_traceback = str_exception(last_exception) if last_exception else 'retry_exc'
            entry_point = retry_state.fn.__name__
            error_message = f"Retry final attempt {attempt_number=}, {entry_point=}, {exc_traceback=}"
            logger.error(error_message)
    return log_after_retry


def retry_factory(logger, max_attempts=3):
    retry_params = dict(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        before_sleep=_before_sleep_factory(logger),
        after=_after_retry_factory(logger),
    )
    return retry(**retry_params)

