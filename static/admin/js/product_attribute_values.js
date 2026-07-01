(function () {
    "use strict";

    const VALUE_FIELDS = [
        "option",
        "value_number",
        "value_bool",
        "value_text",
    ];
    const TYPE_FIELD_MAP = {
        choice: "option",
        number: "value_number",
        boolean: "value_bool",
        bool: "value_bool",
        text: "value_text",
    };
    const META_CACHE = new Map();
    const HIDDEN_CLASS = "product-attribute-value-field-hidden";

    function getProductAdminBaseUrl() {
        const marker = "/main_app/product/";
        const index = window.location.pathname.indexOf(marker);

        if (index === -1) {
            return null;
        }

        return window.location.pathname.slice(0, index + marker.length);
    }

    function getMetaUrl(attributeId) {
        const baseUrl = getProductAdminBaseUrl();

        if (!baseUrl) {
            return null;
        }

        return `${baseUrl}attribute-meta/${attributeId}/`;
    }

    function getInlineRow(element) {
        return element.closest(".inline-related, tr.form-row");
    }

    function getFieldContainer(row, fieldName) {
        return row.querySelector(`.field-${fieldName}`);
    }

    function getFieldInput(row, fieldName) {
        const container = getFieldContainer(row, fieldName);

        if (!container) {
            return null;
        }

        return container.querySelector("select, input, textarea");
    }

    function setFieldVisible(row, fieldName, visible) {
        const container = getFieldContainer(row, fieldName);

        if (!container) {
            return;
        }

        container.classList.toggle(HIDDEN_CLASS, !visible);
    }

    function clearInput(input) {
        if (!input) {
            return;
        }

        if (input.tagName === "SELECT") {
            input.value = "";

            if (input.value !== "" || input.selectedIndex < 0) {
                input.selectedIndex = 0;
            }

            input.dispatchEvent(new Event("change", { bubbles: true }));
            return;
        }

        if (input.type === "checkbox" || input.type === "radio") {
            input.checked = false;
            input.dispatchEvent(new Event("change", { bubbles: true }));
            return;
        }

        input.value = "";
        input.dispatchEvent(new Event("input", { bubbles: true }));
    }

    function clearValueFields(row) {
        VALUE_FIELDS.forEach((fieldName) => {
            clearInput(getFieldInput(row, fieldName));
        });
    }

    function fillOptionSelect(row, options, shouldClear) {
        const select = getFieldInput(row, "option");

        if (!select) {
            return;
        }

        const previousValue = shouldClear ? "" : select.value;
        select.innerHTML = "";

        const emptyOption = document.createElement("option");
        emptyOption.value = "";
        emptyOption.textContent = "---------";
        select.appendChild(emptyOption);

        options.forEach((option) => {
            const element = document.createElement("option");
            element.value = String(option.id);
            element.textContent = option.value;
            select.appendChild(element);
        });

        select.value = previousValue;

        if (previousValue && select.value !== previousValue) {
            select.value = "";
        }
    }

    async function fetchAttributeMeta(attributeId) {
        if (META_CACHE.has(attributeId)) {
            return META_CACHE.get(attributeId);
        }

        const metaUrl = getMetaUrl(attributeId);

        if (!metaUrl) {
            return null;
        }

        const response = await fetch(metaUrl, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
            credentials: "same-origin",
        });

        if (!response.ok) {
            return null;
        }

        const meta = await response.json();
        META_CACHE.set(attributeId, meta);
        return meta;
    }

    function hideValueFields(row) {
        VALUE_FIELDS.forEach((fieldName) => {
            setFieldVisible(row, fieldName, false);
        });
    }

    async function updateRow(row, shouldClear) {
        const attributeInput = getFieldInput(row, "attribute");
        const attributeId = attributeInput ? attributeInput.value : "";

        hideValueFields(row);

        if (!attributeId) {
            if (shouldClear) {
                clearValueFields(row);
            }

            return;
        }

        row.dataset.productAttributeValueAttributeId = attributeId;

        if (shouldClear) {
            clearValueFields(row);
        }

        const meta = await fetchAttributeMeta(attributeId);

        if (!meta) {
            return;
        }

        const visibleField = TYPE_FIELD_MAP[meta.type];

        if (!visibleField) {
            return;
        }

        if (visibleField === "option") {
            fillOptionSelect(row, meta.options || [], shouldClear);
        }

        setFieldVisible(row, visibleField, true);
    }

    function initRow(row) {
        if (!row || row.dataset.productAttributeValuesInitialized === "true") {
            return;
        }

        row.dataset.productAttributeValuesInitialized = "true";
        updateRow(row, false);
    }

    function initAllRows() {
        document
            .querySelectorAll(".inline-related .field-attribute select, tr.form-row .field-attribute select")
            .forEach((attributeInput) => {
                initRow(getInlineRow(attributeInput));
            });
    }

    function handleAttributeChange(attributeInput) {
        const row = getInlineRow(attributeInput);

        if (row) {
            const currentAttributeId = attributeInput.value || "";
            const previousAttributeId = row.dataset.productAttributeValueAttributeId || "";
            const shouldClear = (
                previousAttributeId !== ""
                && previousAttributeId !== currentAttributeId
            );

            updateRow(row, shouldClear);
        }
    }

    function bindDjangoJQueryEvents() {
        const djangoJQuery = window.django && window.django.jQuery;

        if (!djangoJQuery || document.documentElement.dataset.productAttributeValuesJqueryBound) {
            return;
        }

        document.documentElement.dataset.productAttributeValuesJqueryBound = "true";

        djangoJQuery(document).on(
            "change select2:select select2:clear",
            ".field-attribute select",
            function () {
                handleAttributeChange(this);
            }
        );
    }

    document.addEventListener("change", (event) => {
        if (event.target.matches(".field-attribute select")) {
            handleAttributeChange(event.target);
        }
    });

    document.addEventListener("formset:added", (event) => {
        initRow(event.target);
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
            bindDjangoJQueryEvents();
            initAllRows();
            window.setTimeout(initAllRows, 100);
        });
    } else {
        bindDjangoJQueryEvents();
        initAllRows();
        window.setTimeout(initAllRows, 100);
    }
})();
