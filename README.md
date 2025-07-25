
# ShopLift - An ecommerce website


## Tools
- Django REST Framework
- Flask
- PostgreSQL
- Swagger
- Docker
## Architecture
This project follows a microservices architecture. It is divided into 5 different services.

![High level architecture](/readme/architecture.png)

## Database design
Since this project has a microservice architecture, each service has an isolated database. This practice reduces the load on the database and also increases the fault tolerance of the system.

![Schema design](/readme/schema.png)
## Implementation
### User service
This service is built with the Django REST Framework. It includes two applications - `core` and `connection`. The `core` application handles all the api calls and views related to the user service.
The `connection` application acts as a gateway for communication with other 4 services. This is because a user never directly interacts with other services, they only interact with them through the user service. All the webpages are rendered from the user service. The authentication and authorization is done by utilizing the default Django user authentication and authorization.
The database for this service has the following models - `User`, `User Role`, `Address`.

### Product service
This service is built with the Django REST Framework. It includes two applications - `products` and `inventory`. The `products` application handles all the api calls to this service. It also has the `Product` model. The `inventory` application has the `InventoryItem` model.

### Cart service
This service is built with the Flask Framework. It handles the database operations with SQLAlchemy. It has the `CartItem` model.

### Order service
This service is built with the Django REST Framework. It includes two applications - `orders` and `transactions`. The `orders` application handles all the api calls to this service. It has the `Order` and `OrderItem` models. Currently, there is no functional transaction handling. It is just mocked by dummy function within the `orders` application. The `transactions` application has the `Transaction` model.

### Review service
This service is built with the Flask Framework. It handles the database operation with SQLAlchemy and it has the `Review` model.
