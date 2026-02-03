(function(){
  const qs = s => document.querySelector(s);
  const qsa = s => Array.from(document.querySelectorAll(s));

  // Mobile menu
  const mobileToggle = qs('#mobile-menu-toggle');
  const mobileMenu = qs('#mobile-menu');
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', () => mobileMenu.classList.toggle('hidden'));
  }

  // Account dropdown
  const accountToggle = qs('#account-toggle');
  const accountMenu = qs('#account-menu');
  if (accountToggle && accountMenu) {
    accountToggle.addEventListener('click', () => accountMenu.classList.toggle('hidden'));
    document.addEventListener('click', (e)=>{
      if(!accountMenu.contains(e.target) && !accountToggle.contains(e.target)){
        accountMenu.classList.add('hidden');
      }
    });
  }

  // Filter drawer
  const drawer = qs('#filter-drawer');
  const openDrawer = qs('#filter-drawer-toggle');
  const closeDrawer = qs('#filter-drawer-close');
  if (drawer && openDrawer) {
    openDrawer.addEventListener('click', ()=> drawer.classList.toggle('hidden'));
    if (closeDrawer) closeDrawer.addEventListener('click', ()=> drawer.classList.add('hidden'));
    drawer?.addEventListener('click', (e)=>{ if(e.target === drawer) drawer.classList.add('hidden'); });
  }

  // Gallery thumbnails
  const mainImage = qs('#main-image');
  qsa('#thumbs .thumb').forEach(btn => {
    btn.addEventListener('click', ()=>{
      const src = btn.dataset.src;
      if(src && mainImage){ mainImage.src = src; }
      qsa('#thumbs .thumb').forEach(b=>b.classList.remove('border-emerald-500','active'));
      btn.classList.add('border-emerald-500','active');
    });
  });

  // Accordion
  qsa('[data-accordion-toggle]').forEach((toggle, idx)=>{
    toggle.addEventListener('click', ()=>{
      const body = toggle.nextElementSibling;
      if(body){ body.classList.toggle('hidden'); }
    });
  });

  // Quantity steppers
  qsa('[data-qty]').forEach(wrapper => {
    const input = wrapper.querySelector('input[type="number"]');
    wrapper.querySelectorAll('[data-qty-increase]').forEach(btn=>btn.addEventListener('click',()=>{
      input.value = parseInt(input.value || '1') + 1;
    }));
    wrapper.querySelectorAll('[data-qty-decrease]').forEach(btn=>btn.addEventListener('click',()=>{
      const next = Math.max(1, parseInt(input.value || '1') - 1);
      input.value = next;
    }));
  });

  // Password visibility
  qsa('[data-password-toggle]').forEach(btn => {
    btn.addEventListener('click', ()=>{
      const wrapper = btn.closest('[data-password-wrapper]');
      const input = wrapper?.querySelector('input');
      if (!input) return;
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.textContent = isHidden ? '?????' : '?????';
    });
  });

  // Close messages
  qsa('.message-close').forEach(btn => btn.addEventListener('click', ()=>{
    btn.parentElement?.remove();
  }));
})();
