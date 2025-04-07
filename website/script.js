// BiasDetector Website Scripts

document.addEventListener('DOMContentLoaded', function() {
  // Initialize Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 70, // Adjust for fixed navbar
          behavior: 'smooth'
        });
        
        // Update URL without page jump
        history.pushState(null, null, targetId);
      }
    });
  });
  
  // Add active class to nav links on scroll
  window.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    let currentSection = '';
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 100;
      const sectionHeight = section.clientHeight;
      
      if (pageYOffset >= sectionTop && pageYOffset < sectionTop + sectionHeight) {
        currentSection = section.getAttribute('id');
      }
    });
    
    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${currentSection}`) {
        link.classList.add('active');
      }
    });
  });
  
  // Toggle navbar background on scroll
  const navbar = document.querySelector('.navbar');
  
  window.addEventListener('scroll', function() {
    if (window.scrollY > 50) {
      navbar.classList.add('navbar-dark', 'bg-dark', 'shadow');
    } else {
      navbar.classList.remove('shadow');
    }
  });
  
  // Form submission handling for contact form (if added later)
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Collect form data
      const formData = new FormData(contactForm);
      const formObject = Object.fromEntries(formData.entries());
      
      // Show loading state
      const submitButton = contactForm.querySelector('button[type="submit"]');
      const originalButtonText = submitButton.innerHTML;
      submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...';
      submitButton.disabled = true;
      
      // You would typically send this data to a backend API
      // For now, we'll just simulate a response after a delay
      setTimeout(() => {
        // Reset form
        contactForm.reset();
        
        // Show success message
        const alertContainer = document.createElement('div');
        alertContainer.className = 'alert alert-success alert-dismissible fade show mt-3';
        alertContainer.role = 'alert';
        alertContainer.innerHTML = `
          <strong>Thank you!</strong> Your message has been sent.
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        contactForm.appendChild(alertContainer);
        
        // Reset button
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
        
        // Auto-dismiss the alert after 5 seconds
        setTimeout(() => {
          const bsAlert = new bootstrap.Alert(alertContainer);
          bsAlert.close();
        }, 5000);
      }, 1500);
    });
  }
  
  // Add installation button functionality
  const installButton = document.querySelector('#install a.btn-primary');
  if (installButton) {
    installButton.addEventListener('click', function(e) {
      e.preventDefault();
      
      // For now, this would redirect to the Chrome Web Store when available
      // or show installation instructions
      const installModal = new bootstrap.Modal(document.getElementById('installModal') || document.createElement('div'));
      if (document.getElementById('installModal')) {
        installModal.show();
      } else {
        alert('Chrome extension coming soon to the Chrome Web Store. For now, please follow the manual installation instructions below.');
      }
    });
  }
  
  // Lazy loading for images
  const lazyImages = document.querySelectorAll('img[loading="lazy"]');
  
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          imageObserver.unobserve(img);
        }
      });
    });
    
    lazyImages.forEach(img => {
      imageObserver.observe(img);
    });
  } else {
    // Fallback for browsers that don't support IntersectionObserver
    lazyImages.forEach(img => {
      img.src = img.dataset.src;
    });
  }
});
