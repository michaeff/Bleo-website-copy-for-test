// static/js/viewer_detail.js
document.addEventListener("DOMContentLoaded", () => {
  // Figure out which week we're on
  const match = window.location.pathname.match(/week\/(\d+)/);
  const WEEK = match ? parseInt(match[1], 10) : null;
  console.log("🔍 Detail viewer for week:", WEEK);

  if (WEEK === null) {
    console.error("Could not determine week from URL");
    return;
  }

  // Find all section containers and set up viewers for each
  const sections = document.querySelectorAll('.section-container');
  console.log(`Found ${sections.length} sections`);

  sections.forEach((section, index) => {
    const viewer = section.querySelector('.czi-viewer');
    const slider = section.querySelector('.z-slider');
    const zlabel = section.querySelector('.z-value');
    const checkboxes = section.querySelectorAll('.channel-cbx');
    const sectionName = section.dataset.section;

    console.log(`Setting up section: ${sectionName}`);

    if (!viewer || !slider || !zlabel || !checkboxes.length) {
      console.error(`Missing elements in section ${sectionName}`);
      return;
    }

    // Show initial slider value
    zlabel.textContent = slider.value;

    // Whenever slider moves
    slider.addEventListener("input", () => {
      zlabel.textContent = slider.value;
      refreshViewer(section, sectionName);
    });

    // Whenever any checkbox changes
    checkboxes.forEach(cbx => {
      console.log(`✅ Wiring checkbox for channel ${cbx.dataset.chan} in section ${sectionName}`);
      cbx.addEventListener("change", () => {
        console.log(`☑️ Channel ${cbx.dataset.chan} now ${cbx.checked} in section ${sectionName}`);
        refreshViewer(section, sectionName);
      });
    });

    // Initial load
    refreshViewer(section, sectionName);
  });

  function refreshViewer(section, sectionName) {
    const viewer = section.querySelector('.czi-viewer');
    const slider = section.querySelector('.z-slider');
    const checkboxes = section.querySelectorAll('.channel-cbx');
    
    const z = slider.value;

    checkboxes.forEach(cbx => {
      const chan = cbx.dataset.chan;
      let img = viewer.querySelector(`img[data-chan="${chan}"]`);

      if (cbx.checked) {
        if (!img) {
          console.log(`➕ Creating IMG for channel ${chan} in section ${sectionName}`);
          img = document.createElement("img");
          img.dataset.chan = chan;
          img.classList.add("chan-img");
          viewer.appendChild(img);
        }

        const sectionFile = sectionName.replace(/-/g, "_");
        let src;
        console.log({sectionName, sectionFile, WEEK, z});

        if (WEEK === 0) {
        if (sectionName === "week0") {
        // Week 0 special case
        src = `/static/processed_detailed/week${WEEK}/week${WEEK}_z${z}_ch${chan}.png`;
        } else {
        // Week 0 overview case (underscore folder + filename)
        src = `/static/overview_processed_detailed/${sectionFile}/overview_${sectionFile}_z${z}_ch${chan}.png`;
        }
        } else {
        // Weeks >= 1
        src = `/static/processed_detailed/week${WEEK}/${sectionName}/week${WEEK}_${sectionName}_z${z}_ch${chan}.png`;
        }


        console.log(`🔗 Loading ${src}`);
        img.src = src;
        img.hidden = false;

        // Handle load errors
        img.onerror = () => {
          console.warn(`Failed to load: ${src}`);
          img.hidden = true;
        };
      } else if (img) {
        console.log(`➖ Hiding channel ${chan} in section ${sectionName}`);
        img.hidden = true;
      }
    });
  }
});

