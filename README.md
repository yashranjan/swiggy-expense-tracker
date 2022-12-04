# Swiggy Expense Tracker

Forked from [swiggy-total-spend](https://github.com/teja156/swiggy-total-spent)!!

The swiggy script retrieves all your swiggy orders and calculates the total money you spent on [swiggy.com](https://www.swiggy.com), along with number of orders and average, and it also generates a example XLS sheet with in-depth data such as who, where, when, how much, delivery time etc.

# How to use

The script expects you to give your swiggy session as input.

- Login to swiggy.com(chrome or firefox)
- Install the [Cookie Editor chrome extension](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm?hl=en) or the [Cookie Editor firefox extension](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)
- Go to the Swiggy tab or Zomato tab and click on the Extension's icon, and select "Export". This will copy your cookies to clipboard
  ![Cookie Editor Extension](assets/screenshot.png 'Text to show on mouseover')
- Create a new file called `cookies.json` in the same directory as the `swiggy.py` script and paste the copied cookies into this file.
- Install requirements with `pip`
  ```
  pip3 install -r requirements.txt
  ```
- Now simply run the Make target to get swiggy orders

  ```
  make gen_data
  ```
