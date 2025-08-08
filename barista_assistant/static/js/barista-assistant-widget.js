// barista-assistant-widget.js - Enhanced Version with Height Management & Centered Layout
(function () {
  const apiBase = "https://apps.techwithwayne.com/api";
  // Create toggle button
  const toggleButton = document.createElement("button");
  toggleButton.id = "barista-assistant-toggle";
  toggleButton.textContent = "☕";
  document.body.appendChild(toggleButton);
  // Create chat container
  const chatContainer = document.createElement("div");
  chatContainer.id = "barista-assistant-container";
  chatContainer.style.display = "none";
  document.body.appendChild(chatContainer);
  // Enhanced styles for centered layout
  const style = document.createElement("style");
  style.textContent = `
  body {
    margin: 0;
    padding: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #121212;
    font-family: 'Segoe UI', sans-serif;
    overflow: hidden; /* Prevent outer scrollbars on the page body */
  }
  #barista-assistant-toggle {
    position: fixed;
    bottom: 20px; /* Positioned at bottom right for standard chat bubble placement */
    right: 20px;
    background-color: #c00000;
    color: white;
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    font-size: 24px;
    cursor: pointer;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
  }
  #barista-assistant-toggle:hover {
    transform: scale(1.1);
    background-color: #e00000;
  }
  #barista-assistant-container {
    width: 90%;
    max-width: 450px;
    height: auto;
    max-height: 580px;
    background: #121212;
    color: white;
    border-radius: 16px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.4);
    overflow-y: auto;
    padding: 16px;
    z-index: 9999;
    font-family: 'Segoe UI', sans-serif;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    margin: 20px auto;
    position: relative;
  }
  .msg {
    background: #1e1e1e;
    margin: 6px 0;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 14px;
    line-height: 1.4;
    box-sizing: border-box;
    animation: fadeIn 0.3s ease-out;
  }
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  .input-row {
    width: 100%;
    margin: 8px 0;
    box-sizing: border-box;
  }
  .input-row input {
    width: 100%;
    padding: 12px;
    border-radius: 8px;
    border: none;
    font-size: 14px;
    background: #2a2a2a;
    color: white;
    box-sizing: border-box;
  }
  .input-row input:focus {
    outline: none;
    box-shadow: 0 0 0 2px #ff6c00;
  }
  .input-row button,
  .menu-item-btn {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    background: #ff6c00;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.3s ease;
    box-sizing: border-box;
  }
  .input-row button:hover,
  .menu-item-btn:hover {
    background: #e65a00;
  }
  .input-row button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  /* Scrollbar styling */
  #barista-assistant-container::-webkit-scrollbar {
    width: 6px;
  }
  #barista-assistant-container::-webkit-scrollbar-track {
    background: #2a2a2a;
    border-radius: 3px;
  }
  #barista-assistant-container::-webkit-scrollbar-thumb {
    background: #ff6c00;
    border-radius: 3px;
  }
  #barista-assistant-container::-webkit-scrollbar-thumb:hover {
    background: #e65a00;
  }
  @media (max-width: 480px) {
    #barista-assistant-container {
      width: 95%;
      max-width: 100%;
      margin: 10px auto;
    }
  }
`;
  document.head.appendChild(style);
  // IframeHeightManager class
  class IframeHeightManager {
    constructor() {
      this.lastHeight = 0;
      this.resizeObserver = null;
      this.debounceTimeout = null;
      this.init();
    }
    init() {
      console.log('📏 Initializing iframe height manager for Barista widget');
      this.startHeightMonitoring();
      setTimeout(() => {
        this.sendHeightToParent();
      }, 1000);
    }
    startHeightMonitoring() {
      // Use ResizeObserver if available
      if (window.ResizeObserver) {
        this.resizeObserver = new ResizeObserver(entries => {
          this.debounceHeightUpdate();
        });
       
        const container = document.getElementById('barista-assistant-container');
        if (container) {
          this.resizeObserver.observe(container);
        }
        this.resizeObserver.observe(document.body);
      }
      // Monitor DOM changes
      const observer = new MutationObserver((mutations) => {
        let shouldUpdate = false;
        mutations.forEach((mutation) => {
          if (mutation.type === 'childList' ||
              mutation.type === 'attributes' ||
              mutation.type === 'subtree') {
            shouldUpdate = true;
          }
        });
       
        if (shouldUpdate) {
          this.debounceHeightUpdate();
        }
      });
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
      });
      // Periodic height check
      setInterval(() => {
        this.sendHeightToParent();
      }, 3000);
    }
    debounceHeightUpdate() {
      if (this.debounceTimeout) {
        clearTimeout(this.debounceTimeout);
      }
     
      this.debounceTimeout = setTimeout(() => {
        this.sendHeightToParent();
      }, 150);
    }
    getOptimalHeight() {
      const bodyScrollHeight = document.body.scrollHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const windowHeight = window.innerHeight;
      const container = document.getElementById('barista-assistant-container');
     
      let containerHeight = 0;
      if (container && container.style.display !== 'none') {
        const rect = container.getBoundingClientRect();
        containerHeight = rect.height;
      }
      const maxHeight = Math.max(
        bodyScrollHeight,
        documentHeight,
        windowHeight,
        containerHeight
      );
      const finalHeight = Math.max(400, maxHeight + 50);
      return Math.min(finalHeight, 800);
    }
    sendHeightToParent() {
      const newHeight = this.getOptimalHeight();
     
      if (Math.abs(newHeight - this.lastHeight) > 15) {
        this.lastHeight = newHeight;
       
        try {
          const heightMessage = {
            type: 'resize',
            height: newHeight,
            timestamp: Date.now(),
            source: 'barista-widget'
          };
          window.parent.postMessage(heightMessage, '*');
          window.parent.postMessage({
            type: 'iframeResize',
            height: newHeight,
            timestamp: Date.now(),
            source: 'barista-widget'
          }, '*');
         
          console.log(`📤 Sent height to parent: ${newHeight}px`);
        } catch (error) {
          console.warn('Failed to send height to parent:', error);
        }
      }
    }
    triggerHeightUpdate() {
      setTimeout(() => {
        this.sendHeightToParent();
      }, 100);
    }
    forceHeightUpdate() {
      this.lastHeight = 0;
      this.sendHeightToParent();
    }
  }
  // Initialize height manager
  let heightManager = null;
 
  // Toggle button event with height management
  toggleButton.addEventListener("click", () => {
    chatContainer.style.display =
      chatContainer.style.display === "none" ? "flex" : "none";
   
    if (chatContainer.style.display === "flex") {
      if (!chatContainer.dataset.initialized) {
        initializeChat();
        chatContainer.dataset.initialized = "true";
      }
     
      // Trigger height update when showing
      if (heightManager) {
        heightManager.forceHeightUpdate();
      }
    }
  });
  // Auto-open on page load
  window.addEventListener("load", () => {
    setTimeout(() => {
      chatContainer.style.display = "flex";
      if (!chatContainer.dataset.initialized) {
        initializeChat();
        chatContainer.dataset.initialized = "true";
      }
     
      // Initialize height manager after opening
      if (!heightManager) {
        heightManager = new IframeHeightManager();
        window.baristaHeightManager = heightManager;
      } else {
        heightManager.forceHeightUpdate();
      }
    }, 500);
  });
  // CSRF helper for Django
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie("csrftoken");
  async function initializeChat() {
    addMessage("👋 Hi, I'm your Barista Assistant. Let's place your order!");
    const customerFirstNameInput = createInput("First Name");
    const customerLastNameInput = createInput("Last Name");
    const customerEmailInput = createInput("Your Email");
    const pickupTimeInput = createInput("Pickup Time (e.g., YYYY-MM-DDTHH:MM)", "datetime-local"); // Clarified placeholder for datetime-local
    chatContainer.appendChild(customerFirstNameInput);
    chatContainer.appendChild(customerLastNameInput);
    chatContainer.appendChild(customerEmailInput);
    chatContainer.appendChild(pickupTimeInput);
    const submitCustomerBtn = createButton("Continue to Menu");
    chatContainer.appendChild(submitCustomerBtn);
    // Trigger height update after adding elements
    if (heightManager) {
      heightManager.triggerHeightUpdate();
    }
    submitCustomerBtn.addEventListener("click", async () => {
      const customerFirstName = customerFirstNameInput
        .querySelector("input")
        .value.trim();
      const customerLastName = customerLastNameInput
        .querySelector("input")
        .value.trim();
      const customerEmail = customerEmailInput
        .querySelector("input")
        .value.trim();
      const pickupTimeRaw = pickupTimeInput.querySelector("input").value;
      if (
        !customerFirstName ||
        !customerLastName ||
        !customerEmail ||
        !pickupTimeRaw
      ) {
        addMessage("⚠️ Please complete all fields to continue.");
        return;
      }
      let pickupTimeFormatted = pickupTimeRaw;
      if (!pickupTimeRaw.endsWith("Z")) {
        pickupTimeFormatted = pickupTimeRaw + ":00Z";
      }
      const pickupTime = new Date(pickupTimeFormatted).toISOString();
      const menu = await fetchMenu();
      if (menu.length === 0) {
        addMessage("⚠️ Menu is currently unavailable.");
        return;
      }
      addMessage("✅ Select an item to add to your order:");
      menu.forEach((item) => {
        const btn = createButton(`${item.name} - $${item.price}`);
        btn.classList.add("menu-item-btn");
        btn.addEventListener("click", () => {
          const order = {
            customer_first_name: customerFirstName,
            customer_last_name: customerLastName,
            customer_email: customerEmail,
            pickup_time: pickupTime,
            order_items: [{ item: item.name, quantity: 1, price: item.price }],
          };
          sendOrder(order);
        });
        chatContainer.appendChild(btn);
      });
      submitCustomerBtn.disabled = true;
     
      // Trigger height update after adding menu items
      if (heightManager) {
        heightManager.triggerHeightUpdate();
      }
    });
  }
  function createInput(placeholder, type = "text") {
    const div = document.createElement("div");
    div.className = "input-row";
    const input = document.createElement("input");
    input.placeholder = placeholder;
    input.type = type;
    div.appendChild(input);
    return div;
  }
  function createButton(text) {
    const btn = document.createElement("button");
    btn.textContent = text;
    return btn;
  }
  function addMessage(text) {
    const msg = document.createElement("div");
    msg.className = "msg";
    msg.textContent = text;
    chatContainer.appendChild(msg);
    chatContainer.scrollTop = chatContainer.scrollHeight;
   
    // Trigger height update after adding message
    if (heightManager) {
      heightManager.triggerHeightUpdate();
    }
  }
  async function fetchMenu() {
    try {
      const res = await fetch(`${apiBase}/menu/`);
      return await res.json();
    } catch (e) {
      console.error(e);
      return [];
    }
  }
  async function sendOrder(order) {
    try {
      const res = await fetch(`${apiBase}/order/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        credentials: "same-origin",
        body: JSON.stringify(order),
      });
      if (res.ok) {
        const data = await res.json();
        addMessage("✅ Order created! Redirecting to payment...");
        await redirectToStripeCheckout(data.id);
      } else {
        addMessage("⚠️ Failed to place order.");
      }
    } catch (e) {
      console.error(e);
      addMessage("⚠️ Error placing order.");
    }
  }
  async function redirectToStripeCheckout(orderId) {
    try {
      console.log("🟡 Starting Stripe checkout for order:", orderId);
      const res = await fetch(`${apiBase}/create-checkout-session/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        credentials: "same-origin",
        body: JSON.stringify({ order_id: orderId }),
      });
      const data = await res.json();
      console.log("🟢 Stripe session response:", data);
      if (!data.id) {
        console.error("❌ Stripe session ID missing from response:", data);
        addMessage("⚠️ Stripe session creation failed.");
        return;
      }
      const keyRes = await fetch(`${apiBase}/stripe/publishable-key/`);
      const keyData = await keyRes.json();
      console.log("🟢 Stripe publishable key response:", keyData);
      if (!keyData.publishableKey) {
        console.error("❌ Stripe publishableKey is missing:", keyData);
        addMessage("⚠️ Stripe key fetch failed.");
        return;
      }
      // Load Stripe.js if not already present
      if (typeof Stripe === "undefined") {
        console.log("🧪 Loading Stripe.js...");
        await new Promise((resolve, reject) => {
          const script = document.createElement("script");
          script.src = "https://js.stripe.com/v3/";
          script.onload = resolve;
          script.onerror = reject;
          document.head.appendChild(script);
        });
        console.log("🧠 Stripe.js loaded.");
      }
      const stripe = Stripe(keyData.publishableKey);
      console.log("🟢 Stripe instance created. Redirecting now...");
      const result = await stripe.redirectToCheckout({ sessionId: data.id });
      if (result.error) {
        console.error(
          "❌ Stripe redirectToCheckout error:",
          result.error.message
        );
        addMessage("⚠️ Redirect error: " + result.error.message);
      } else {
        console.log("✅ Stripe redirect initiated successfully.");
      }
    } catch (e) {
      console.error("🔥 Stripe redirect failed:", e);
      addMessage("⚠️ Failed to redirect to payment.");
    }
  }
  // Handle window resize
  window.addEventListener('resize', () => {
    if (heightManager) {
      heightManager.triggerHeightUpdate();
    }
  });
  // Handle visibility changes
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && heightManager) {
      heightManager.forceHeightUpdate();
    }
  });
  // Handle page show event (back/forward navigation)
  window.addEventListener('pageshow', function(event) {
    if (event.persisted && heightManager) {
      setTimeout(() => {
        heightManager.forceHeightUpdate();
      }, 300);
    }
  });
})();