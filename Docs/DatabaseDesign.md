HomeOS Database Design

Philosophy

HomeOS is designed around simplicity.

The database stores only the information required to support the application today. Future features should be added by extending the schema, not by overcomplicating the initial design.

Core principles:

-Products are generic.
-Inventory tracks quantities.
-Shopping lists track what needs buying.
-Recipes consume products.
-Data should not be duplicated.
-Historical information should be preserved where practical.


---------------------

Products
Purpose

Stores every product known to HomeOS.

A product is simply "a thing".

Examples:

Milk
Chicken
Heinz Beans
Peanut Butter

A product does not contain inventory or shopping information.

Fields
Field	Purpose
ProductID	Primary key
Name	Product name
Notes	Optional notes
CreatedDate	When the product was created
IsActive	Soft delete flag


---------------------


Inventory
Purpose

Tracks how much of each product currently exists.

Inventory references Products.

Inventory should never create duplicate products.

Fields
Field	Purpose
InventoryID	Primary key
ProductID	Product reference
Quantity	Amount owned
Unit	Unit of measurement
UpdatedDate	Last updated
Inventory Transactions
Purpose

Stores every inventory change.

Inventory becomes the current state.

Transactions become the history.

Examples

+2 Milk
-1 Milk
+12 Eggs
-6 Eggs

This allows future reporting such as:

Consumption
Trends
AI predictions
Shopping recommendations

---------------------
Shopping List
Purpose

Represents a shopping session.

Normally only one shopping list will be active.

Old shopping lists are retained for history.

Fields
Field	Purpose
ShoppingListID	Primary key
Name	Optional name
CreatedDate	Created
CompletedDate	Finished
---------------------
Shopping List Items
Purpose

Represents products belonging to a shopping list.

Each item references Products.

Fields
Field	Purpose
ShoppingListItemID	Primary key
ShoppingListID	Shopping list
ProductID	Product
Quantity	Quantity required
Notes	Optional
Purchased	Tick box
---------------------
Recipes
Purpose

Stores recipes.

A recipe is simply instructions plus ingredients.
---------------------
Future Features

Not included in V1.

Possible additions:

Barcode scanning
Price history
Preferred supermarkets
Expiry tracking
Nutrition
AI meal planning
Voice assistant
Kitchen display integration
---------------------