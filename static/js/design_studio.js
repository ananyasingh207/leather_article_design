/**
 * LeatherCraft Designer - Design Studio Interactive Live Preview Engine (Phase 5)
 * Pure Vanilla JavaScript module providing real-time client-side preview manipulation
 */

(function () {
    'use strict';

    // Centralized Color & Style Maps
    const LEATHER_COLOR_MAP = {
        'Black': { bg: '#1c1c1c', border: '#111111', textShadow: 'rgba(255,255,255,0.15)' },
        'Brown': { bg: '#5c3a21', border: '#3e2413', textShadow: 'rgba(0,0,0,0.4)' },
        'Tan': { bg: '#c68b59', border: '#a56c3e', textShadow: 'rgba(0,0,0,0.3)' },
        'Dark Brown': { bg: '#3b2214', border: '#26140a', textShadow: 'rgba(0,0,0,0.5)' },
        'Red': { bg: '#8b261d', border: '#5e150f', textShadow: 'rgba(0,0,0,0.4)' },
        'Blue': { bg: '#1c3b57', border: '#102436', textShadow: 'rgba(0,0,0,0.4)' }
    };

    const STITCH_COLOR_MAP = {
        'Black': '#111111',
        'White': '#f8f8f8',
        'Brown': '#7a4b27',
        'Tan': '#d9a066',
        'Red': '#c0392b'
    };

    const FONT_STYLE_MAP = {
        'Classic': 'Cinzel, Georgia, serif',
        'Modern': 'Inter, "Helvetica Neue", sans-serif',
        'Elegant': '"Playfair Display", "Times New Roman", serif',
        'Bold': 'Impact, "Arial Black", sans-serif'
    };

    // Centralized Live Preview State Object
    const previewState = {
        color: 'Brown',
        finish: 'Matte',
        stitching: 'Brown',
        text: '',
        font: 'Classic',
        textSize: 18,
        positionX: 50,
        positionY: 50,
        rotation: 0,
        side: 'front',
        width: 11.5,
        height: 9.0,
        depth: 2.0,
        category: 'Wallets'
    };

    // Initial Form Values on page load
    const initialFormValues = {
        name: '',
        type: 'Full Grain Leather',
        color: 'Brown',
        finish: 'Matte',
        stitching: 'Brown',
        text: '',
        font: 'Classic',
        textSize: '18',
        width: '11.5',
        height: '9.0',
        depth: '2.0'
    };

    // DOM Elements Cache
    let elements = {};

    function cacheDOMElements() {
        elements = {
            // Form Inputs
            nameInput: document.getElementById('id_name'),
            typeSelect: document.getElementById('id_leather_type'),
            colorSelect: document.getElementById('id_leather_color'),
            finishSelect: document.getElementById('id_leather_finish'),
            stitchSelect: document.getElementById('id_stitching_color'),
            textInput: document.getElementById('id_custom_text'),
            fontSelect: document.getElementById('id_font'),
            sizeSelect: document.getElementById('id_text_size'),
            widthInput: document.getElementById('id_width'),
            heightInput: document.getElementById('id_height'),
            depthInput: document.getElementById('id_depth'),

            // Interactive Sliders & Badges
            sliderPosX: document.getElementById('sliderPosX'),
            sliderPosY: document.getElementById('sliderPosY'),
            sliderRotation: document.getElementById('sliderRotation'),
            badgePosX: document.getElementById('badgePosX'),
            badgePosY: document.getElementById('badgePosY'),
            badgeRotation: document.getElementById('badgeRotation'),

            // Side Buttons & Reset
            sideTabs: document.querySelectorAll('.btn-side-tab'),
            resetBtn: document.getElementById('btnResetPreview'),

            // Preview Stage DOM
            canvasStage: document.getElementById('studioCanvasStage'),
            articleBody: document.getElementById('articleLeatherBody'),
            stitchFrame: document.getElementById('articleStitchFrame'),
            embossText: document.getElementById('liveEmbossElement'),
            watermark: document.getElementById('articleWatermark'),

            // Readouts
            readoutColor: document.getElementById('readoutColor'),
            readoutStitching: document.getElementById('readoutStitching'),
            readoutDimensions: document.getElementById('readoutDimensions'),
            readoutFinish: document.getElementById('readoutFinish')
        };
    }

    /**
     * Stores the initial values rendered by Django on page load.
     */
    function captureInitialValues() {
        if (elements.nameInput) initialFormValues.name = elements.nameInput.value;
        if (elements.typeSelect) initialFormValues.type = elements.typeSelect.value;
        if (elements.colorSelect) initialFormValues.color = elements.colorSelect.value;
        if (elements.finishSelect) initialFormValues.finish = elements.finishSelect.value;
        if (elements.stitchSelect) initialFormValues.stitching = elements.stitchSelect.value;
        if (elements.textInput) initialFormValues.text = elements.textInput.value;
        if (elements.fontSelect) initialFormValues.font = elements.fontSelect.value;
        if (elements.sizeSelect) initialFormValues.textSize = elements.sizeSelect.value;
        if (elements.widthInput) initialFormValues.width = elements.widthInput.value;
        if (elements.heightInput) initialFormValues.height = elements.heightInput.value;
        if (elements.depthInput) initialFormValues.depth = elements.depthInput.value;
    }

    /**
     * Updates the leather body color, border, and finish highlights.
     */
    function updateLeather() {
        if (!elements.articleBody) return;

        const colorConfig = LEATHER_COLOR_MAP[previewState.color] || LEATHER_COLOR_MAP['Brown'];
        elements.articleBody.style.backgroundColor = colorConfig.bg;
        elements.articleBody.style.borderColor = colorConfig.border;

        // Finish treatment
        if (previewState.finish === 'Glossy') {
            elements.articleBody.style.boxShadow = 'inset 0 3px 12px rgba(255,255,255,0.3), 0 12px 28px rgba(0,0,0,0.3)';
        } else if (previewState.finish === 'Textured') {
            elements.articleBody.style.boxShadow = 'inset 0 0 16px rgba(0,0,0,0.45), 0 10px 24px rgba(0,0,0,0.22)';
        } else if (previewState.finish === 'Smooth') {
            elements.articleBody.style.boxShadow = 'inset 0 1px 4px rgba(255,255,255,0.15), 0 12px 28px rgba(0,0,0,0.22)';
        } else {
            // Matte
            elements.articleBody.style.boxShadow = '0 10px 24px rgba(0,0,0,0.2)';
        }

        if (elements.readoutColor) elements.readoutColor.textContent = previewState.color;
        if (elements.readoutFinish) elements.readoutFinish.textContent = previewState.finish;
    }

    /**
     * Updates the perimeter stitching line color.
     */
    function updateStitching() {
        if (!elements.stitchFrame) return;

        const stitchColor = STITCH_COLOR_MAP[previewState.stitching] || '#7a4b27';
        elements.stitchFrame.style.borderColor = stitchColor;

        if (elements.readoutStitching) elements.readoutStitching.textContent = previewState.stitching;
    }

    /**
     * Safely updates embossed monogram text, typography style, size, position, and rotation.
     */
    function updateText() {
        if (!elements.embossText) return;

        const textContent = previewState.text ? previewState.text.trim() : '';

        if (textContent) {
            // Safe DOM insertion preventing XSS injection
            elements.embossText.textContent = textContent;
            elements.embossText.style.opacity = '1';
        } else {
            elements.embossText.textContent = '';
            elements.embossText.style.opacity = '0';
        }

        // Font Family & Size
        elements.embossText.style.fontFamily = FONT_STYLE_MAP[previewState.font] || 'Cinzel, Georgia, serif';
        elements.embossText.style.fontSize = previewState.textSize + 'px';

        // Position & Rotation transforms
        elements.embossText.style.left = previewState.positionX + '%';
        elements.embossText.style.top = previewState.positionY + '%';
        elements.embossText.style.transform = `translate(-50%, -50%) rotate(${previewState.rotation}deg)`;

        // Update Slider Value Badges
        if (elements.badgePosX) elements.badgePosX.textContent = `X: ${previewState.positionX}%`;
        if (elements.badgePosY) elements.badgePosY.textContent = `Y: ${previewState.positionY}%`;
        if (elements.badgeRotation) elements.badgeRotation.textContent = `Rotation: ${previewState.rotation}°`;
    }

    /**
     * Adjusts the preview body proportions dynamically based on dimensions.
     */
    function updateDimensions() {
        if (!elements.articleBody) return;

        const w = parseFloat(previewState.width) || 12.0;
        const h = parseFloat(previewState.height) || 9.0;
        const d = parseFloat(previewState.depth) || 2.0;

        if (elements.readoutDimensions) {
            elements.readoutDimensions.textContent = `${w} × ${h} × ${d} cm`;
        }

        // Proportional scaling within bounded canvas viewport (only in front/back views)
        if (previewState.side !== 'side') {
            const aspect = w / (h || 1);
            let baseWidth = 280;
            let baseHeight = Math.round(baseWidth / aspect);

            // Clamp dimensions to safe bounds
            if (baseHeight > 240) {
                baseHeight = 240;
                baseWidth = Math.round(baseHeight * aspect);
            }
            if (baseWidth > 360) {
                baseWidth = 360;
                baseHeight = Math.round(baseWidth / aspect);
            }
            if (baseWidth < 140) baseWidth = 140;
            if (baseHeight < 60) baseHeight = 60;

            elements.articleBody.style.width = baseWidth + 'px';
            elements.articleBody.style.height = baseHeight + 'px';
        }
    }

    /**
     * Toggles product view side (Front, Back, Side).
     */
    function updateSide(sideName) {
        previewState.side = sideName;

        if (elements.canvasStage) {
            elements.canvasStage.classList.remove('view-front', 'view-back', 'view-side');
            elements.canvasStage.classList.add(`view-${sideName}`);
        }

        // Update tab buttons active class
        if (elements.sideTabs) {
            elements.sideTabs.forEach(tab => {
                if (tab.getAttribute('data-side') === sideName) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });
        }

        // Refresh dimensions for side view
        updateDimensions();
    }

    /**
     * Master orchestrator function.
     */
    function updatePreview() {
        updateLeather();
        updateStitching();
        updateText();
        updateDimensions();
    }

    /**
     * Resets all preview controls and form inputs back to the initial values.
     */
    function resetPreview() {
        // 1. Restore Form Input Fields
        if (elements.typeSelect && initialFormValues.type) elements.typeSelect.value = initialFormValues.type;
        if (elements.colorSelect && initialFormValues.color) elements.colorSelect.value = initialFormValues.color;
        if (elements.finishSelect && initialFormValues.finish) elements.finishSelect.value = initialFormValues.finish;
        if (elements.stitchSelect && initialFormValues.stitching) elements.stitchSelect.value = initialFormValues.stitching;
        if (elements.textInput) elements.textInput.value = initialFormValues.text || '';
        if (elements.fontSelect && initialFormValues.font) elements.fontSelect.value = initialFormValues.font;
        if (elements.sizeSelect && initialFormValues.textSize) elements.sizeSelect.value = initialFormValues.textSize;
        if (elements.widthInput && initialFormValues.width) elements.widthInput.value = initialFormValues.width;
        if (elements.heightInput && initialFormValues.height) elements.heightInput.value = initialFormValues.height;
        if (elements.depthInput && initialFormValues.depth) elements.depthInput.value = initialFormValues.depth;

        // 2. Reset Interactive Sliders & Badges
        previewState.positionX = 50;
        previewState.positionY = 50;
        previewState.rotation = 0;

        if (elements.sliderPosX) elements.sliderPosX.value = 50;
        if (elements.sliderPosY) elements.sliderPosY.value = 50;
        if (elements.sliderRotation) elements.sliderRotation.value = 0;

        // 3. Reset to Front View
        updateSide('front');

        // 4. Re-sync previewState from restored form inputs and re-render
        readFormValues();
        updatePreview();
    }

    /**
     * Synchronizes previewState from the active Django form inputs.
     */
    function readFormValues() {
        if (elements.colorSelect) previewState.color = elements.colorSelect.value;
        if (elements.finishSelect) previewState.finish = elements.finishSelect.value;
        if (elements.stitchSelect) previewState.stitching = elements.stitchSelect.value;
        if (elements.textInput) previewState.text = elements.textInput.value;
        if (elements.fontSelect) previewState.font = elements.fontSelect.value;
        if (elements.sizeSelect) previewState.textSize = parseInt(elements.sizeSelect.value, 10) || 18;
        if (elements.widthInput) previewState.width = parseFloat(elements.widthInput.value) || 12.0;
        if (elements.heightInput) previewState.height = parseFloat(elements.heightInput.value) || 9.0;
        if (elements.depthInput) previewState.depth = parseFloat(elements.depthInput.value) || 2.0;
    }

    /**
     * Initializes the Design Studio live preview.
     */
    function initializePreview() {
        cacheDOMElements();

        if (!elements.canvasStage) {
            // Not on Design Studio page
            return;
        }

        // Read article category from container data attribute
        const category = elements.canvasStage.getAttribute('data-category') || 'Wallets';
        previewState.category = category;

        // Capture initial form values on page load
        captureInitialValues();

        // Read active form values
        readFormValues();

        // Attach event listeners to standard form controls
        const formControls = [
            elements.colorSelect,
            elements.finishSelect,
            elements.stitchSelect,
            elements.textInput,
            elements.fontSelect,
            elements.sizeSelect,
            elements.widthInput,
            elements.heightInput,
            elements.depthInput
        ];

        formControls.forEach(ctrl => {
            if (ctrl) {
                ctrl.addEventListener('input', () => {
                    readFormValues();
                    updatePreview();
                });
                ctrl.addEventListener('change', () => {
                    readFormValues();
                    updatePreview();
                });
            }
        });

        // Attach event listeners to interactive sliders
        if (elements.sliderPosX) {
            elements.sliderPosX.addEventListener('input', (e) => {
                previewState.positionX = parseInt(e.target.value, 10);
                updateText();
            });
        }

        if (elements.sliderPosY) {
            elements.sliderPosY.addEventListener('input', (e) => {
                previewState.positionY = parseInt(e.target.value, 10);
                updateText();
            });
        }

        if (elements.sliderRotation) {
            elements.sliderRotation.addEventListener('input', (e) => {
                previewState.rotation = parseInt(e.target.value, 10);
                updateText();
            });
        }

        // Side selector tabs
        if (elements.sideTabs) {
            elements.sideTabs.forEach(tab => {
                tab.addEventListener('click', (e) => {
                    e.preventDefault();
                    const side = tab.getAttribute('data-side');
                    if (side) updateSide(side);
                });
            });
        }

        // Reset Preview Button
        if (elements.resetBtn) {
            elements.resetBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                resetPreview();
            });
        }

        // Initial render
        updateSide('front');
        updatePreview();
    }

    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializePreview);
    } else {
        initializePreview();
    }

})();
