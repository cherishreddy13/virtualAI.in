// light and dark mode 
const toggle = document.getElementById('themeToggle');

toggle.addEventListener('change', () => {
   document.body.style.backgroundColor = toggle.checked ? '#000000' : '#FFFFFF'; // Night and Day background
   document.body.style.color = toggle.checked ? 'white' : 'black'; // Adjust text color
});
// ends here
