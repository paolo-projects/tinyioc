Usage
=====

.. contents::

Getting started
---------------

To install the library:

.. code-block::

   $ pip install tinyioc

Description
-----------

The injection system is based on a few but important concepts.

First, there's the container (IocContainer) singleton object which
has the responsibility of directing classes registration and injection.

The **container** is generally never directly accessed, instead the use of
decorators is strongly encouraged. **Decorators** help write cleaner code and
avoid writing the registration logic directly.

Decorators also allow for classes with constructor arguments to be injected
as a singleton or transient, by specifying the constructor arguments into the
decorator.

**Modules** are fundamental when you need to scope your dependencies. Say,
for instance, that you need the same service to have two different instances
for two separate purposes, then modules are the solution.
By registering one instance into one module, and the other instance into
the other module, you can easily decide which instance gets injected where.

- **Container**

  Classes must be registered inside the container.
  The container is a singleton object that can be accessed globally, taking care
  of registering the services into the modules, and retrieving them when needed.

- **Modules**

  Modules are a sort of "scope" for services, so that you can register the same
  service multiple times, with different arguments, into different modules.

Service can be registered in three ways, so that you can choose the pattern
that most fits your style:

- by using the procedural way through the helper methods (`register_instance`,
  `register_singleton`, `register_transient`)
- by using the `@injectable` decorator
- by declaring the dependencies into the `provides` property inside the module

Injection
---------

Injection works in two phases:

1. The service must be registered into the appropriate module through
   the container, the decorators or the module
2. The service is injected from the right module into a function, or can be
   retrieved manually through the `get_service` helper function

Registration
------------

The services can be registered by using decorators on classes (or functions),
or by manually calling the helper methods.

Let's see some examples for the first case:

- Classes can be automatically registered into the container through the `@injectable()` decorator:

.. code-block::

  @injectable(ServiceLifetime.SINGLETON)
  class MailService:
      ...

- Class constructor arguments can be passed through the decorator:

.. code-block::

  @injectable(base_url="/api", timeout=3000)
  class ApiService:
      def __init__(self, base_url: str, timeout: int):
          ...

.. code-block::

  @injectable(base_url=app_configuration.base_url, timeout=app_configuration.timeout)
  class ApiService:
      def __init__(self, base_url: str, timeout: int):
          ...

Here's some examples using the helper methods:

- Registering an instance

.. code-block::

  service = ApiService(base_url=url, timeout=3000, ...)
  register_instance(service)

- You can also register your class using the class name. It will be
  instantiated as soon as it is requested:

.. code-block::

  register_singleton(ApiService, base_url=url, timeout=3000)

- When using this method, the class can be registered both as a singleton
  (same instance available throughout the whole app), or as a transient
  service (new instance every time it is injected):

.. code-block::

  register_transient(DatabaseService, host="localhost", ...)

And to retrieve the service:

.. code-block::

   service = get_service(ApiService)

Modules
-------

All the previous methods registered the classes into a `GlobalModule`, available by default.

Suppose you want to register a class twice, with different parameters for different needs.
Or you may have different sections of your app that need a different instance of the singleton service.

Modules are the answer to this necessity. With modules, you can scope your services and have control over
where the dependency comes from. Additionally, modules are very easy to implement and use.

To declare a module you define a class inheriting from `IocModule` and adding the `@module()` decorator:

.. code-block::

   @module()
   class MyModule(IocModule):
     pass

Registering classes into a specific module is very easy. You use the same decorator as before, additionally
specifying the `module` parameter:

.. code-block::

   @injectable(module=MyModule)
   class MyService:
    ...

or, if injecting an instance of your class, by specifying the `module` parameter:

.. code-block::

   register_instance(FileSystemService(root="/opt/myapp"), MyModule)

An alternative is to use the declarative way of providing services from a module,
by defining the `provides` property:

.. code-block::

   @module()
   class MyModule(IocModule):
       provides = [
         ProvideInstance(ApiService(base_url="/api")),
         ProvideSingleton(DatabaseService, host="localhost", database="mydb"),
         ProvideTransient(TokenService)
       ]

Dependency injection
--------------------

You can inject any service into any function through the decorator:

.. code-block::

   @inject()
   def my_api_route(database_service: DatabaseService):
       products = database_service.get_products()
    ...

You can also inject multiple services:

.. code-block::

   @inject()
   def my_api_route(authentication_service: AuthenticationService,
                    database_service: DatabaseService):
       if (authentication_service.is_authenticated()):
           cart = database_service.get_cart(authentication_service.get_user_id())
           ...

Transform a getter function into an injected property
_____________________________________________________

Class member functions (or plain functions) can be transformed into injected getter methods through
the `@inject_getter()` decorator. You only need to specify the right return type:

.. code-block::

   class MyClass:
       @inject_getter()
       def get_service_a(self) -> ServiceA:
           pass

The `get_service_a()` method, annotated with the appropriate return type, will return the injected service.

Injection into injected services
________________________________

You can inject services into another service by using the decorator on the constructor:

.. code-block::

   class ServiceA:
       ...

   class ServiceB:
       @inject()
       def __init__(self, service_a: ServiceA):
           self.service_a = service_a
           ...

   register_singleton(ServiceA)
   # ServiceB will automatically be injected ServiceA into the constructor
   register_singleton(ServiceB)

   @inject()
   def my_function(service_b: ServiceB):
       ...

Beware, though, that this strategy could lead to an injection loop. Make sure that classes
injected into other classes are not circularly dependent, or you will get
an infinite loop trying to instantiate them, like in this example:

.. code-block::

   class ServiceA:
       @inject()
       def __init__(self, service_b: ServiceB):
           ...

   class ServiceB:
       @inject()
       def __init__(self, service_a: ServiceA):
           ...

   register_singleton(ServiceA)
   register_singleton(ServiceB)

   # A circular injection loop happens here!!!
   # When injecting ServiceB, ServiceA will be instantiated, and during
   # its instantiation, ServiceB will be instantiated again, which in turn
   # will instantiate ServiceA again and so on until everything breaks!
   @inject()
   def my_function(service_b: ServiceB):
       ...

This issue happens only when injecting into the constructor, or into a method called by the
constructor. If you need to access a service from another service you can inject it into
a class getter through the `inject_getter()` decorator:

.. code-block::

   class ServiceA:
       @inject_getter()
       def service_b(self) -> ServiceB:
           pass

   class ServiceB:
       @inject()
       def __init__(self, service_a: ServiceA):
           ...

Modules
_______

Injecting the dependency from the right module is straightforward. You only need to specify the module in the
decorator parameter:

.. code-block::

   @inject(MyModule)
   def my_function(service: MyService):
       ...

You can also specify the module for each dependency through the `FromModule` helper class:

.. code-block::

   @inject()
   def my_function(svc_a: MyService = FromModule(ModuleA),
                   svc_b: MyService = FromModule(ModuleB))
     ...

Function injection
__________________

You can also inject a function's result into other functions:

.. code-block::

   # you can use it as a generator
   @injectable(ServiceLifetime.TRANSIENT)
   def generate_token():
       return uuid.uuid4()

   @inject()
   def my_fun(token: generate_token):
       # token will contain the random
       # token generated through the function

       # being injected transient, it is equivalent to this:
       other_token = generate_token()
       ...

   # or as a provider
   @injectable(ServiceLifetime.SINGLETON)
   def provide_database():
       return ...

   @inject()
   def my_fun_2(db: provide_database):
       db.execute("INSERT INTO ...")

Interfaces
----------

As many already know, python doesn't have interfaces, but we can use abstract classes
and class inheritance to obtain the same result. TinyIOC supports registering a service
instance or class as an interface class, so to have the maximum flexibility in the injection
system.

For instance, let's suppose you have a base class that defines an interface for an API service,
and one or more concrete implementations.

.. code-block::

    class CollectionsRepository(object):
        def get_collections(self) -> List[Collection]:
            pass

        def get_collection(self, id: int) -> Optional[Collection]:
            pass

    class ApiCollectionsRepository(CollectionsRepository):
        ...

You can register the concrete implementation, the ``ApiCollectionsRepository``, as
the abstract parent class, the ``CollectionsRepository``, making it easy to switch
to another implementation in a second time.

.. code-block::

    @injectable(register_for=CollectionsRepository)
    class ApiCollectionsRepository(CollectionsRepository):
        ...

As a module dependency:

.. code-block::

    @module()
    class MyModule(IocModule):
        provides = [
            ProvideInstance(ApiCollectionsRepository(), provide_for=CollectionsRepository)
        ]

Or programmatically:

.. code-block::

    register_instance(ApiCollectionsRepository(), register_for=CollectionsRepository)

-----

You can then inject this service referring to the abstract class:

.. code-block::

    @inject()
    def my_function(collections: CollectionsRepository):
        ...

Example
-------

Decorators
__________

**Service**

.. code-block::

   @injectable()
   class AuthenticationService:
       @inject()
       def __init__(self, database: DatabaseService):
           ...

**Using it...**

.. code-block::

   @inject()
   def login(authentication_service: AuthenticationService, ...):
       result = authentication_service.login(user, password)
    ...

Declarative
___________

**Service**

.. code-block::

   class AuthenticationService:
       @inject()
       def __init__(self, database: DatabaseService):
           ...

**Module**

.. code-block::

   @module()
   class ApplicationModule(IocModule):
       provides = [
         ProvideSingleton(AuthenticationService)
       ]

**Using it...**

.. code-block::

   @inject(ApplicationModule)
   def login(authentication_service: AuthenticationService, ...):
       result = authentication_service.login(user, password)
       ...
