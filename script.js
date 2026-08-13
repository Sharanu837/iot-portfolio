document.addEventListener("DOMContentLoaded", () => {
  const track = document.getElementById("sliderTrack");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  let currentPosition = 0;
  const cardWidth = 320; // Card width + gap

  nextBtn.addEventListener("click", () => {
    // Prevent sliding beyond the 8th card
    const maxScroll = -(cardWidth * 5); 
    if (currentPosition > maxScroll) {
      currentPosition -= cardWidth;
      track.style.transform = `translateX(${currentPosition}px)`;
    }
  });

  prevBtn.addEventListener("click", () => {
    if (currentPosition < 0) {
      currentPosition += cardWidth;
      track.style.transform = `translateX(${currentPosition}px)`;
    }
  });
});
document.getElementById('connectBtn').addEventListener('click', function() {
    // 1. Smooth scroll to projects section
    document.getElementById('projects').scrollIntoView({ behavior: 'smooth' });
    
    // 2. Futuristic Alert Message
    alert("SYSTEM CONNECTED: All 8 Computer Vision Nodes Online!");
});
