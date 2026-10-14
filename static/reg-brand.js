/* ============================================================
   Radiant Energy Group — brand tokens for scripts + Chart.js defaults.
   Purpose: one palette for every chart, map and inline colour. Values are read
   from the CSS custom properties in static/reg.css (Brandbook v2 p8), so the
   hex codes live in exactly one place.
   Load AFTER reg.css (so the variables resolve) and AFTER Chart.js (if used).
   ============================================================ */
(function () {
    var root = document.documentElement;
    function v(name) { return getComputedStyle(root).getPropertyValue(name).replace(/\s+/g, ' ').trim(); }

    var MAP = {
        yellow: '--reg-yellow',            ochre: '--reg-yellow-accent',
        greyLight: '--reg-grey-light',     greyDark: '--reg-grey-dark',
        cobalt: '--reg-blue-cobalt',       navy: '--reg-cobalt-accent',
        vermilion: '--reg-vermilion',      brown: '--reg-vermilion-accent',
        powder: '--reg-blue-powder',       slate: '--reg-powder-accent',
        forest: '--reg-green-forest',      forestDark: '--reg-forest-accent',
        sage: '--reg-green-sage',          sageDark: '--reg-sage-accent',
        powderHover: '--reg-powder-hover',
        text: '--text-primary',            text2: '--text-secondary',
        muted: '--text-muted',             hairline: '--hairline',
        grid: '--chart-grid',              danger: '--danger',
        cardAlt: '--bg-card-alt',
        fontText: '--font-text',           fontDisplay: '--font-display',
        fontMicro: '--font-micro'
    };
    var REG = {};
    Object.keys(MAP).forEach(function (k) {
        Object.defineProperty(REG, k, { get: function () { return v(MAP[k]); }, enumerable: true });
    });
    /* REG.rgba('cobalt', 0.1) -> "rgba(63, 85, 195, 0.1)" */
    REG.rgba = function (key, alpha) {
        var h = (REG[key] || key).replace('#', '');
        if (h.length === 3) h = h.replace(/(.)/g, '$1$1');
        var n = parseInt(h, 16);
        return 'rgba(' + (n >> 16 & 255) + ', ' + (n >> 8 & 255) + ', ' + (n & 255) + ', ' + alpha + ')';
    };
    /* Categorical order for multi-series charts: brand colours first, then the p8 accents. */
    Object.defineProperty(REG, 'categorical', {
        get: function () {
            return [REG.cobalt, REG.forest, REG.vermilion, REG.sage, REG.yellow,
                    REG.powder, REG.navy, REG.brown, REG.slate, REG.ochre];
        }
    });
    window.REG = REG;

    if (window.Chart) {
        var d = Chart.defaults;
        d.font.family = REG.fontText;
        d.color = REG.text2;
        d.borderColor = REG.grid;
        d.plugins.legend.labels.color = REG.greyDark;
        d.plugins.tooltip.backgroundColor = REG.greyDark;
        d.plugins.tooltip.titleFont = { family: REG.fontText, weight: 'bold' };
        d.plugins.tooltip.bodyFont = { family: REG.fontText };
        d.plugins.tooltip.cornerRadius = 0;
        d.elements.bar.borderRadius = 0;          /* square, solid blocks (p13) */
        /* Redraw once the web font has arrived, so no chart keeps a fallback face. */
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(function () {
                Object.values(Chart.instances || {}).forEach(function (c) { c.update('none'); });
            });
        }
    }
})();
