# 🛒 My Store - CS50W Final Project

## General Description
This project is an e-commerce web application built with **Django on the backend** and **JavaScript on the frontend**, designed to allow users to browse products, add them to a dynamic shopping cart, filter by categories in real time, and even generate a direct **WhatsApp link** containing their order details.  

The application is designed to be **responsive**, so it works seamlessly on both mobile devices and desktop.  

It incorporates key features of a real e-commerce system, but with a focus on **frontend interactivity** and **backend persistence**.  

---

## Distinctiveness and Complexity
This project is **sufficiently distinct** from prior CS50W assignments because it is neither a simple social network (like Project 4) nor just a generic e-commerce system (like Project 2). Here are the main points that highlight its **distinctiveness** and **complexity**:

1. **WhatsApp integration as a sales channel**:  
   Users can generate a dynamic link containing the details of their shopping cart to continue the purchase directly through WhatsApp. This integration is not present in previous projects and provides an alternative checkout flow, especially useful in local markets.

2. **Dynamic shopping cart with JavaScript**:  
   The cart does not require page reloads. It uses **AJAX and the fetch API** to update quantities, remove products, and recalculate the total in real time. The cart’s state is persisted within the Django session.

3. **Category system with dynamic loading**:  
   When clicking on a category, products are loaded dynamically via JSON, avoiding full page reloads and improving the user experience.

4. **Real-time search**:  
   Includes a search bar that filters products as the user types, responding with JSON data and updating the DOM through JavaScript.

5. **Product view and click counters**:  
   Each product tracks how many times it has been viewed and clicked, useful for analytics or product prioritization.

6. **Modern and responsive design**:  
   The project includes a **custom JavaScript carousel system**, in addition to styled components with Bootstrap and a **handmade toast notification system** implemented on the frontend.

Altogether, these features demonstrate a **higher level of complexity** than standard projects because they combine:  
- **Server-side logic (Django, sessions, relational models).**  
- **Advanced dynamic frontend (DOM API, fetch, events, custom notifications).**  
- **Data persistence (Product and Category models, view/click metrics).**  
- **External service integration (WhatsApp as a checkout method).**  

---

## File Structure

### Backend (Django)
- **models.py**  
  Defines `Product` and `Category` models, with attributes such as price, stock, images, views, and clicks.
  
- **views.py**  
  Contains the project logic:
  - `homepage`: renders products and categories.  
  - `product_detail`: shows product details and related products.  
  - `add_to_cart`, `remove_from_cart`, `decrease_quantity`, `get_cart_data`: API for managing the cart.  
  - `categoria`: loads products by category via JSON.  
  - `search_products` and `search_products_page`: implement dynamic search and search results page.  
  - `whatsapp_link`: generates the direct link to send orders through WhatsApp.  
  - `ask_for_stock`: allows users to ask about product availability via WhatsApp.  

- **templates/**  
  - `layout.html`: base template with header, footer, and offcanvas cart.  
  - `homepage.html`: main view with category and featured product carousels.  
  - `product_detail.html`: page for an individual product.  
  - `search_results.html`: search results page.  

### Frontend (JavaScript)
- **scripts.js**:  
  - Functions `addToCart`, `removeFromCart`, `updateCartUI` to handle the dynamic cart.  
  - Notification system (`showMessage`).  
  - Dynamic category loading and live search.  
  - Carousel control with prev/next buttons.  

### Additional Files
- **requirements.txt**: contains the required dependencies (e.g., Django, Pillow for images).  
- **static/**: images, CSS styles, and frontend JavaScript.  

---

## How to Run the Application

1. **Clone the repository**:
   ```bash
   git clone <repo_url>
   cd my_store
