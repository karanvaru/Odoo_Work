/** @odoo-module **/
import { viewService } from "@web/views/view_service";
import { deepCopy } from "@web/core/utils/objects";
import { registry } from "@web/core/registry";
import { generateLegacyLoadViewsResult } from "@web/legacy/legacy_load_views";


viewService.start = function (env, { orm }) {
    let cache = {};

    env.bus.addEventListener("CLEAR-CACHES", () => {
        cache = {};
        const processedArchs = registry.category("__processed_archs__");
        processedArchs.content = {};
        processedArchs.trigger("UPDATE");
    });

    /**
     * Loads fields information
     *
     * @param {string} resModel
     * @param {LoadFieldsOptions} [options]
     * @returns {Promise<object>}
     */
    async function loadFields(resModel, options = {}) {
        const key = JSON.stringify([
            "fields",
            resModel,
            options.fieldNames,
            options.attributes,
        ]);
        if (!cache[key]) {
            cache[key] = orm
                .call(resModel, "fields_get", [options.fieldNames, options.attributes])
                .catch((error) => {
                    delete cache[key];
                    return Promise.reject(error);
                });
        }
        return cache[key];
    }
    /**
     * Load Records
     * Inherited to load records in domain widget
     */
    async function loadRecords(resModel, options = {}) {
        const args = {
            domain: [],
            fields: ["id", "display_name"],
            context: { ...this.extraContext, web_domain_widget: true},
        }
        const key = JSON.stringify([
            "records",
            resModel,
            options.fieldNames,
            options.attributes,
        ]);
        cache[key] = orm.call(resModel, "domain_search_read", [], args).catch((error) => {
            delete cache[key];
            return Promise.reject(error);
        });

        return cache[key];
    }
    /**
     * Loads various information concerning views: fields_view for each view,
     * fields of the corresponding model, and optionally the filters.
     *
     * @param {LoadViewsParams} params
     * @param {LoadViewsOptions} [options={}]
     * @returns {Promise<ViewDescriptions>}
     */
    async function loadViews(params, options = {}) {
        const loadViewsOptions = {
            action_id: options.actionId || false,
            load_filters: options.loadIrFilters || false,
            toolbar: options.loadActionMenus || false,
        };
        if (env.isSmall) {
            loadViewsOptions.mobile = true;
        }
        const { context, resModel, views } = params;
        const filteredContext = Object.fromEntries(
            Object.entries(context || {}).filter((k, v) => !String(k).startsWith("default_"))
        );
        const key = JSON.stringify([resModel, views, filteredContext, loadViewsOptions]);
        if (!cache[key]) {
            cache[key] = orm
                .call(resModel, "get_views", [], { context, views, options: loadViewsOptions })
                .then((result) => {
                    const { models, views } = result;
                    const modelsCopy = deepCopy(models); // for legacy views
                    
                    const viewDescriptions = {
                        __legacy__: generateLegacyLoadViewsResult(resModel, views, modelsCopy),
                        fields: models[resModel],
                        relatedModels: models,
                        views: {},
                    };
                    for (const [resModel, fields] of Object.entries(modelsCopy)) {
                        const key = JSON.stringify(["fields", resModel, undefined, undefined]);
                        cache[key] = Promise.resolve(fields);
                    }
                    for (const viewType in views) {
                        const { arch, toolbar, id, filters, custom_view_id } = views[viewType];
                        const viewDescription = { arch, id, custom_view_id };
                        if (toolbar) {
                            viewDescription.actionMenus = toolbar;
                        }
                        if (filters) {
                            viewDescription.irFilters = filters;
                        }
                        viewDescriptions.views[viewType] = viewDescription;
                    }
                    return viewDescriptions;
                })
                .catch((error) => {
                    delete cache[key];
                    return Promise.reject(error);
                });
        }
        return cache[key];
    }
    return { loadViews, loadFields, loadRecords};
}
