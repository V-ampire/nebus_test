from typing import Callable, Any, Type
import inspect


class DIContainer:
    def __init__(self):
        self._registrations: dict[Type, Callable] = {}
        self._singletons: dict[Type, Any] = {}
        self._singleton_instances: dict[Type, Any] = {}

    def register(self, cls: Type, factory: Callable = None):
        """Register dependency."""
        self._registrations[cls] = factory or cls

    def register_singleton(self, cls: Type, factory: Callable = None):
        """Register singleton."""
        if cls in self._singletons or cls in self._singleton_instances:
            raise ValueError(f'{factory} is already registered as singleton.')
        self._singletons[cls] = factory or cls

    def register_instance(self, cls: Type, instance: Any):
        """Register singleton instance."""
        if cls in self._singletons or cls in self._singleton_instances:
            raise ValueError(f'{cls} is already registered as singleton.')
        self._singleton_instances[cls] = instance
        self._singletons[cls] = cls

    def resolve(
        self,
        cls: Type,
        *,
        depends: dict[Type, Any] | None = None,
        options: dict[str, Any] | None = None,
        common_options: dict[str, Any] | None = None,
    ) -> Any:
        """
        Resolve dependency.
        Args:
            - depends - dependency provided in depends it has priority to use
            - options - options for cls, has higher priority against common_options
            - common_options - options for all nested depends.
        """
        return self._resolve_internal(
            cls, depends or {}, options or {}, common_options or {}, set()
        )

    def _resolve_internal(
        self,
        cls: Type,
        depends: dict[Type, Any],
        options: dict[str, Any],
        common_options: dict[str, Any],
        stack: set
    ) -> Any:
        options = {**common_options, **options} # options for cls, has higher priority against common_options
        if cls in self._singleton_instances:
            return self._singleton_instances[cls]

        if cls in depends:
            return depends[cls]

        factory = self._registrations.get(cls) or self._singletons.get(cls)
        if not factory:
            raise ValueError(f"Dependency {cls} is not registered")

        # Avoid cycling
        if cls in stack:
            raise ValueError(f"Cyclic dependency detected for {cls}")
        stack.add(cls)

        sig = inspect.signature(factory)
        resolved_args = {}

        for name, param in sig.parameters.items():
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                raise ValueError(
                    f"Missing type annotation for parameter '{name}' in {cls}")

            if name in options:
                # use options
                resolved_args[name] = options[
                    name]
            elif param_type in depends:
                resolved_args[name] = depends[param_type]
            # depends is singletons
            elif param_type in self._singleton_instances:
                resolved_args[name] = self._singleton_instances[param_type]
            elif param_type in self._registrations or param_type in self._singletons:
                resolved_args[name] = self._resolve_internal(
                    param_type,
                    depends,
                    {},
                    common_options,
                    stack
                )
            elif param.default != inspect.Parameter.empty:
                resolved_args[name] = param.default
            else:
                raise ValueError(
                    f"Cannot resolve parameter '{name}' for {cls}")

        stack.remove(cls)
        instance = factory(**resolved_args)

        if cls in self._singletons:
            self._singleton_instances[cls] = instance

        return instance
