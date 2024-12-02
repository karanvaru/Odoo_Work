/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
// import { symmetricalDifference } from "../core/utils/arrays";

var rpc = require('web.rpc');

function parseCompanyIds(cidsFromHash) {
    const cids = [];
    if (typeof cidsFromHash === "string") {
        cids.push(...cidsFromHash.split(",").map(Number));
    } else if (typeof cidsFromHash === "number") {
        cids.push(cidsFromHash);
    }
    return cids;
}

function getAvailableBranch(cids,user_Id) {  
    return new Promise((resolve,reject)=>{
        rpc.query({
            model: 'res.users',
            method: 'availableBranch',
            args: [{'cids':cids,'user_id':user_Id}],
        }).then((response)=>{
            console.log("========getAvailableBranch",response)
            resolve(response)
        })
    })
}

function computeAllowedBranchIds(availableBranches){
    let branchIds = []
    availableBranches.map((branch)=>{
        branchIds.push(branch['id'])
    })
    return branchIds

}

export const BranchService = {
    dependencies: ["user", "router", "cookie"],
    async start(env,{ user, router, cookie }) {
        let cids;
        if ("cids" in router.current.hash) {
            cids = parseCompanyIds(router.current.hash.cids);
        } else if ("cids" in cookie.current) {
            cids = parseCompanyIds(cookie.current.cids);
        }      
        let result_branchess = await getAvailableBranch(cids,session.uid)
        let current_branches = result_branchess[0]
        let availableBranches = result_branchess[1]
        let nowBranch = result_branchess[2]
        return {
            availableBranches,
            get allowedBranchIds() {                
                if (current_branches.length == 0){
                    return [availableBranches[0].id]
                }
                return current_branches;
            },
            get currentBranch() {
                return nowBranch;
            },
            setBranch (mode,branchID){                
                if (mode === 'loginto'){
                    rpc.query({
                        model: 'res.users',
                        method: 'ChangeDefaultBranch',
                        args: [{'branch_id':branchID,'user_id':session.uid}],
                    }).then((response)=>{
                        if (response) {
                            browser.setTimeout(() => browser.location.reload());
                        }                                    
                    })
                }
                
            },
            setBranches(mode, branchId) {
                let nextCompanyIds;
                if (mode === "toggle") {                    
                    rpc.query({
                        model: 'res.users',
                        method: 'ChangeAllowedBranch',
                        args: [{'branch_id':branchId,'user_id':session.uid}],
                    }).then((response)=>{
                        if (response) {
                            browser.setTimeout(() => browser.location.reload());
                        }                                    
                    })
                }
            },
        };
        
    },
};

registry.category("services").add("branch", BranchService);
