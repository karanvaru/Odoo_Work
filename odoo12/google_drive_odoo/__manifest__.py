# -*- coding: utf-8 -*-
{
    "name": "Google Drive Odoo Integration",
    "version": "12.0.1.1.7",
    "category": "Document Management",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/google-drive-odoo-integration-278",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "cloud_base"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {
        "python": []
},
    "summary": "The tool to automatically synchronize Odoo attachments with Google Drive files in both ways",
    "description": """
    Odoo document system is clear and comfortable to use. However, it is not especially designed to work with files as Google Drive does. To process attachments users need to download a file, to change it, and to upload back. Documents are not synced locally and Odoo doesn't have powerful previewers and editors.<br/>
Google Drive doesn't have such disadvantages. This is the tool to integrate their features into your Odoo business work flow. The app automatically stores all Odoo attachments in Google Drive, and it provides an instant access to them via web links. In such a way users work with files comfortably in the cloud storage, while the results are fully available in Odoo.

    Automatic integration
    Bilateral sync
    Sync any documents you like
    Easy accessible files
    Individual and team drives
    Sync logs in Odoo
    Default folders for documents
    Applicable to all Odoo apps
    Compatible with Odoo Enterprise Documents
    # How files and folders are synced from Odoo to Google Drive
    Direct synchronization has 2 prime aims:
<ul>
<li>Prepare and keep updated folders' structure in Google Drive</li>
<li>Upload new attachments to a correct folder</li>
</ul>
<strong>Folders</strong>
<p style="font-size:18px">
Odoo creates a convenient directory structure in Google Drive: Odoo / Document type name / Document name / Files, where:
<ul>
<li><i>Odoo</i> is a central directory for Odoo Sync in your Drive.</li>
<li><i>Document type</i> is a synced Odoo model, for example, 'Sale orders', 'Opportunities', 'Customers' 
<ul>
<li>You select document types by yourself. It might be <strong>any document type</strong></li>
<li>Moreover, you might have <strong>a few folders for a single document type</strong>. Use Odoo domains to have not global 'Partners, but 'Customers' and 'Suppliers', not just 'Sale orders' but 'Commercial offers', 'To deliver', and 'Done orders'</li>
<li>With each sync Odoo would try to update document types' folders. Add a new document type at any moment. It will appear in Google Drive with a next sync</li>

<li>You are welcome to introduce or change document types folder names at any moment in Odoo. Take into account: renaming in Google Drive will be recovered to Odoo names</li>
<li>If you remove a model from integration, it will <strong>not</strong> be deleted from Google Drive to keep already synced files safe. However, new documents of this type would not be synced</li>
<li>In case you removed a directory in Google Drive, but it is still configured in Odoo, with a next sync a folder structure is going to be recovered (not files, surely).</li>
</ul>
</li>
<li><i>Document</i> is an exact object to sync. For instance, 'Agrolait' or 'SO019'
<ul>
<li>Documents are synced in case they relate to a synced document type and satisfy its filters. For example, you are not obliged to sync all partners, you may integrate only 'Customers' and 'Vendors' or only 'Companies', not 'Contacts'</li>
<li>Odoo would generate a folder in Google Drive for each suitable document even for documents without attachments. It is needed for a backward sync to easily add new files</li>
<li>Google Drive folder name equals a real document name. It relies upon Odoo name_get method. Thus, Odoo 'Michael Fletcher' (a contact of 'Agrolait') would be Google Drive 'Agrolait, Michael Fletcher'</li>
<li>If an exact document changes its document type (e.g. a quotation is now confirmed), Odoo will  automatically relocate its related folder to a proper parent directory (in the example: from 'Commercial offers' to 'To deliver')</li>
<li>In case a document relates to a few types (for instance, you have 'Vendors' and 'Customers', while Agrolait is both), this document folder would be put into the most prioritized document type. A document type priority is higher as closer to the top in Odoo interfaces it is</li>
<li>If an Odoo document is removed, the next sync will remove a corresponding Google Drive directory</li>
<li>In case you remove a directory in Google Drive, but it still exists in Odoo, Google Drive folder structure would be recovered (while files would be unlinked in both Odoo and Google Drive)</li>
<li>Folders renaming in Google Drive will be replaced with Odoo names, Odoo document names are  more important</li>
</ul>
</li>
<li><i>Files</i> are real files taken from Odoo attachments</li>
</ul>
</p>
<p style="font-size:18px">
The resulted path would be, for example, 'Odoo / Quotations / SO019 / commercial offer.png'.
</p>
<p style="font-size:18px">
The only exclusion of the rule are <i>stand alone attachments</i> which do not relate to any Odoo documents (their document type is 'ir.attachment'). Such attachments' path is 'Odoo / Stand Alone Attachments / image.png'.
</p>
<p style="font-size:18px">
The very first sync might take quite a long, since a lot of folders should be created. Afterwards, it would be much faster. However, it is not recommended to make sync too frequent: once an hour seems quite good for large files.
</p>
<strong>Files</strong>
<p style="font-size:18px">
With each direct sync, Odoo tries to find not yet synced attachments. If such attachments suit any document type to sync, a file will be uploaded to Google Drive to a proper folder. In Odoo such attachments will become of 'url' type. It means that a file is not any more kept in Odoo server space, but now it is in Google Drive. Until sync is done, Odoo attachment remains binary and stores an actual file. Such approach helps Odoo to work faster.
</p>
<p "font-size:18px">
Clicking on such attachment leads you to a file previewer / editor in Google Drive. Depending on your Google Drive configurations it might be Google Documents, Google Spreadsheets, PDF previewer, etc. Anyway  changes to file contents in Google Drive are available in Odoo at the same moment. 
</p>
<p style="font-size:18px">
If you unlinked an attachment from Odoo, it would be deleted in Google Drive as well.
</p>
<p style="font-size:18px">
Take into account that file names should be managed in Google Drive: each backward sync would recover Google Drive names, Odoo is here less important.
</p>
    # How items are retrieved from Google Drive to Odoo
    Backward integration aims to sync new files from Google Drive to Odoo:
<ul>
<li>If a new file is added to a proper document folder (e.g. to 'Odoo / Customers / Agrolait'), the same attachment will be added to Odoo document (in the example – to 'Agrolait')</li>
<li>In document folders you can put not only files but also <i>child folders</i>. In that case a link for this folder (not its content) is kept in attachments</li>
<li>In case you rename a file in Google Drive, it will be renamed in Odoo as well</li>
<li>Files' removal from Google Drive leads to related Odoo attachments' removal</li>
<li>If you move a file to another document folder, in Odoo a related attachment would be re-attached to this new document. Take into account: if you move a file for a not document folder, in Odoo attachment will be deleted as it has been removed from Google Drive</li>
<li>If you deleted a document type or a document folder, their child files are deleted as well. Thus, Odoo would remove related attachments. The folders, however, will be recovered with a next direct sync. Folders' move to another directory is also considered as a removal. Avoid such situations by following the simple rule: folders are managed mostly by Odoo, files – mostly by Google Drive.</li>
</ul>
<p style="font-size:18px">
Backward Google Drive sync might take quite much time, since each folder should be checked (the more folders, the more time the backward sync requires). It is recommended to make frequency oftener than once an hour or two hours.
</p>
    # Typical use cases
    <ul style='font-size:18px;'>
<li><i>Projects:</i> automatically forward all project-related documents to Google Drive to share those with a customer as a cloud link.</li>
<li><i>Customers</i>: add all partner files in a single directory available both from Odoo and from Google Drive. Modify those using default cloud editors and access them when working in Odoo.</i></li>
<li><i>Employees:</i> gather all files by this employee in a single cloud folder: photos, document scans, contracts. Access and upload those from Odoo and Google Drive alternatively.</li>
<li><i>Opportunities:</i> carefully store all specifications, requirements and any file which would let you make a good offer.</li>
<li><i>Orders:</i> keep all printings and contracts in Google Drive with simple availability from Odoo.</li>
</ul>
    # A few important peculiarities to take into account
    <ul>
<li>Take into account that files or folders deleted in Google Drive are really deleted only when you clean trash. Otherwise, such files still exist and would be reflected in Odoo</li>
<li>Try to avoid the following symbols in folders' and files' names: *, ?, ", ', :, &lt;, &gt;, |, +, %, !, @, \, /,.  Direct sync will replace such symbols with '-'. It is done to avoid conflicts with file systems.</li>
</ul>
    # How Odoo Enterprise Documents are synced
    <p style="font-size:18px">
This tool is not in conflict with the 'documents' module provided by the Enterprise license. Attachments related to Enterprise folders would be synced as any other files: according to a document they relate to. In the most cases it means they would be linked to stand-alone attachments.
</p>
<p style="font-size:18px">
It is not always comfortable, and you might be interested in reflecting directories' structure introduced by the module 'Documents'. To this end the extension <a href='https://apps.odoo.com/apps/modules/12.0/cloud_base_documents/'>Cloud Sync for Enterprise Documents</a> (its standard price is 44 Euros) is developed. This tool has the following features:
</p>
<ul style="font-size:18px">
<li>The documents hierarchy is reflected within the folder 'Odoo / Odoo Docs'</li>
<li>Each Odoo folder has a linked cloud folder. Take into account that folders created in the cloud storage will be synced as Odoo attachments. The key principle is: folders are managed by Odoo, files are managed by the cloud client</li>
<li>All files are synced with the same logic as usual attachments. Files created in Odoo will be added to the cloud storage and will be replaced with links in Odoo. Files created in cloud storage will generate attachments within a paired directory</li>
<li>Please do not name synced models as 'Odoo Docs'. This is the reserved name for Odoo Enterprise Documents</li>
</ul>
    Fast access to Google Drive files and folders
    Synced files are simply found in Google Drive. Add unlimited number of files or folders here
    Choose document types to be synced
    Document type might have a few folders based on filters
    All document types are in the root directory 'Odoo'
    Document types' folders
    All document of this type has an own folder
    Odoo Enterprise documents sync
    Logged synchronisation activities
    Default folders for this document types to be created while firstly synced
    I faced the error: QWeb2: Template 'X' not found
    <div class="knowsystem_block_title_text">
            <div class="knowsystem_snippet_general" style="margin:0px auto 0px auto;width:100%;">
                <table align="center" cellspacing="0" cellpadding="0" border="0" class="knowsystem_table_styles" style="width:100%;background-color:transparent;border-collapse:separate;">
                    <tbody>
                        <tr>
                            <td width="100%" class="knowsystem_h_padding knowsystem_v_padding o_knowsystem_no_colorpicker" style="padding:20px;vertical-align:top;text-align:inherit;">
                                
                                <ol style="margin:0px 0 10px 0;list-style-type:decimal;"><li><p class="" style="margin:0px;">Restart your Odoo server and update the module</p></li><li><p class="" style="margin:0px;">Clean your browser cashe (Ctrl + Shift + R) or open Odoo in a private window.</p></li></ol></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    What are update policies of your tools?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 115% }
	</style>


</p><p lang="en-US" style="margin:0px 0px 0.25cm 0px;line-height:120%;">According to the current Odoo Apps Store policies:</p><ul style="margin:0px 0 10px 0;list-style-type:disc;"><li><p lang="en-US" style="margin:0px;line-height:120%;"> every module bought for the version 12.0 and prior gives you an access to the all versions up to 12.0. </p></li><li><p lang="en-US" style="margin:0px;line-height:120%;">starting from the version 13.0, every version of the module should be purchased separately.</p></li><li><p lang="en-US" style="margin:0px;line-height:120%;">disregarding the version, purchasing a tool grants you a right for all updates and bug fixes within a major version.<br></p></li></ul><p lang="en-US" style="margin:0px 0px 0.25cm 0px;line-height:120%;">Take into account that Odoo Tools team does not control those policies. By all questions please contact the Odoo Apps Store representatives <a href="https://www.odoo.com/contactus" style="text-decoration:none;color:rgb(13, 103, 89);background-color:transparent;">directly</a>.</p>
    May I buy your app from your company directly?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 10px 0px;">Sorry, but no. We distribute the
tools only through the <a href="https://apps.odoo.com/apps" style="text-decoration:none;color:rgb(13, 103, 89);background-color:transparent;">official Odoo apps store</a></p>
    How should I install your app?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="line-height:120%;margin:0px 0px 10px 0px;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><ol style="margin:0px 0 10px 0;list-style-type:decimal;">
	<li><p style="margin:0px;line-height:120%;">Unzip source code of purchased tools in one of your Odoo
	add-ons directory</p>
	</li><li><p style="margin:0px;line-height:120%;">Re-start the Odoo server</p>
	</li><li><p style="margin:0px;line-height:120%;">Turn on the developer mode (technical settings)</p>
	</li><li><p style="margin:0px;line-height:120%;">Update the apps' list (the apps' menu)</p>
	</li><li><p style="margin:0px;line-height:120%;">Find the app and push the button 'Install'</p>
	</li><li><p style="margin:0px;line-height:120%;">Follow the guidelines on the app's page if those exist.</p>
</li></ol>
    Can I have a few folders for the the same document type? For example, internal projects and customer projects?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="line-height:120%;margin:0px 0px 10px 0px;">Yes, you can. To that goal you should prepare a separate sync
model on the configuration tab. Then, for each of those apply
filters: for example by type of a project.</p>
<p style="line-height:120%;margin:0px 0px 10px 0px;">Try to make filters self-exclusive in order a document can be
definitely assigned. For instance, 'customer but not supplier',
'supplier but not customer'. Otherwise, a specific document folder
would jump from one model to another.</p>
    Your tool has dependencies on other app(s). Should I purchase those?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Yes, all modules marked in dependencies are absolutely required for a correct work of our tool. Take into account that price marked on the app page already includes all necessary dependencies.&nbsp;&nbsp;</p>
    May I change frequency of sync jobs?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Yes, you can. To this end:</p><ol style="margin:0px 0 10px 0;list-style-type:decimal;"><li><p style="margin:0px;line-height:120%;">Turn on debug mode</p></li><li><p style="margin:0px;line-height:120%;">Go to technical settings &gt; Automation &gt; Scheduled jobs</p></li><li><p style="margin:0px;line-height:120%;">Find the jobs 'Synchronize attachments with cloud' and 'Update attachments from cloud'.</p></li></ol><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Take into account that you should not make them too frequent. It would be better if that this job should be finished until a new one is started. Thus, the configuration should depend on how many items you to sync you have. Usually, the frequency is set up between 10 minutes to 4 hours.</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Make also sure that you have set up enough time limits in your
Odoo configuration file. Thus, LIMIT_TIME_CPU and LIMIT_TIME_REAL
parameters should be equal or bigger than planned cron job time.</p><p style="line-height:120%;margin:0px 0px 10px 0px;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>










</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">An import notice for Odoo.sh clients: the maximum time for cron
job might be set up as 15 minutes.</p>
    I noticed that your app has extra add-ons. May I purchase them afterwards?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Yes, sure. Take into account that Odoo
automatically adds all dependencies to a cart. You should exclude
previously purchased tools.</p>
    I would like to get a discount
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Regretfully, we do not have a
technical possibility to provide individual prices.</p>
    Is it possible to make synchronization real-time?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">No. We have strong reasons to avoid real time sync:</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>




</p><ul style="margin:0px 0 10px 0;list-style-type:disc;">
	<li><p style="margin:0px;line-height:120%;">Performance issues. In case a sync is real time, each file
	upload will result in the loading screen.</p>
	</li><li><p style="margin:0px;line-height:120%;">Conflict issues. If 2 users simultaneously change an item, it
	might lead to unresolved situations. In case of regular jobs we can
	fix it afterwards, while in case of real time we would need to save
	it as some queue, and it will be even more misleading for users.</p>
	</li><li><p style="margin:0px;line-height:120%;">Functionality issues. In particular, renaming and
	restructuring of items. In the backward sync the tool strictly
	relies upon directories' logic, and during each sync 100% of items
	are checked. In case it is done after each update, it will be
	thousands of requests per second. If not: changes would be lost.</p>
</li></ul><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
    Should I set up specific users accesses in Odoo?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">No, the tool relies upon a single user end point. It means that
all sync processes are done under a single cloud admin (app). Access
rights for created folders / files are not automatized. You should
administrate those rights in your cloud storage solution.</p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;"><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style></p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
    How can I install your app on Odoo.sh?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 10px 0px;">As soon as you purchased the
app, the button 'Deploy on Odoo.sh' will appear on the app's page in
the Odoo store. Push this button and follow the instructions.</p>
<p style="margin:0px 0px 10px 0px;">Take into account that for paid
tools you need to have a private GIT repository linked to your
Odoo.sh projects</p>
    May I install the app on my Odoo Online (SaaS) database?
    <p style="margin:0px 0px 10px 0px;">No, third party apps can not be used on Odoo Online.</p>
    Where would be synced fields stored? Are they duplicated to Odoo and clouds?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">All synced files are kept only in the clouds, in Odoo attachments
become of the URL-type. When a user clicks on those, Odoo would
redirect him/her to a cloud storage.</p><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
    Is it Okay if I had many objects to sync, for example, 10000?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Yes, although in case of many folders / attachments to sync, the
process might be slow. Simultaneously, our clients reported to us the
environments with &gt;10k partners and ~5k product variants to be
synced, and the processes were acceptable.</p>
<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">A few points to emphasize:</p>
<ol style="margin:0px 0 10px 0;list-style-type:decimal;">
	<li><p style="margin:0px;line-height:120%;">The sync is constructed in such a way that anyway any item
	will be synced and will not be lost, although it might be not fast.
	It is guaranteed by first-in-first-out queues and by each job
	commits.</p>
	</li><li><p style="margin:0px;line-height:120%;">The number of objects might be limited logically. The models'
	configuration let you restrict sync of obsolete items (e.g there is
	no sense to sync archived partners or orders which are done 2 years
	ago).</p>
</li></ol>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
    Would standard Odoo preview work for synced items?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">No, since files are now kept in the cloud storage, and retrieving
binary contents would consume a lot of resources. Odoo has a link
which would redirect a user to a proper previewer or editor.</p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
    Would the app work with Odoo 12 Enterprise documents?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">For Odoo v12 Enterprise you have 2 options:</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>



</p><ol style="margin:0px 0 10px 0;list-style-type:decimal;">
	<li><p style="margin:0px;line-height:120%;">To sync only standard documents' attachments, but not to sync
	folders' and files' structure related to the Enterprise module
	'Documents'.</p>
	</li><li><p style="margin:0px;line-height:120%;">To sync both Odoo standard attachments and to reflect
	Enterprise Documents' folders/files. In such a case you need an
	extra add-in <a href="https://apps.odoo.com/apps/modules/12.0/cloud_base_documents/" style="text-decoration:none;color:rgb(13, 103, 89);background-color:transparent;">Cloud
	Sync for Enterprise Documents</a> (44 Euro).</p>
</li></ol>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
    May I change default folders' name in clouds?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">For models' directories (sale orders, opportunities, suppliers,
etc.): you may assign your own name on the configuration tab for any
document type.</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>



</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">For objects' folders (SO-001, John Smith, etc.): the tool relies
upon the Odoo 'name_get' method for this document type. In case you
need to make a different title, you should re-define this method for
a specific model. It requires source code modification.</p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;"><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style></p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
    May I configure different structure of synced directories rather than assumed by sync?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">No, the module works with the pre-defined structure of folders:</p><ol style="margin:0px 0 10px 0;list-style-type:decimal;">
	<li><p style="margin:0px;line-height:120%;">Odoo – a core folder for sync</p>
	</li><li><p style="margin:0px;line-height:120%;">Models – folders for each Odoo document type. For example,
	'Projects', 'Partners'. Distinguished by domain there might be more
	specific folders: e.g., 'Customer 1 Projects', 'Projects of the
	Customer 2', 'Internal Projects', etc.</p>
	</li><li><p style="margin:0px;line-height:120%;">Objects – folders for each document, e.g. 'Project 1' or
	'Customer 1'</p>
	</li><li><p style="margin:0px;line-height:120%;">Files and folders related to this Odoo document to be synced.</p>
</li></ol><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">As a result you may have for instance:</p><ul style="margin:0px 0 10px 0;list-style-type:disc;">
	<li><p style="margin:0px;line-height:120%;">Odoo / Projects / Project 1 / files and folders related to
	the&nbsp; project 1</p>
	</li><li><p style="margin:0px;line-height:120%;">Odoo / Customer 1 Projects / Project 1; Odoo / Customer 2
	Projects / Project 3, ...</p>
	</li><li><p style="margin:0px;line-height:120%;">Odoo / Customers / Customer 1 / files and folders related to
	the customer 1</p>
</li></ul><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>






</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">This structure is always flat, meaning that there are only those
levels of hierarchy. Thus, it is correct that various document types
can't be done within the same structure. Within the folder 'Customer
1' we can't keep the files related both to sale orders, invoices, and
projects. Each of those document type has an own (or a few own)
folders. Otherwise, we will not have a chance to make backward
synchronisation, since there would be no criteria to rely upon.</p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;"><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style></p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
    Do I need only the Cloud Storage Solution app?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">No, the tool is only a technical core. You also need the connector
for your cloud client.</p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;"><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style></p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
    We use a special editor in our clouds (e.g. OnlyOffice, Office 365, etc.). Would files be opened in that editor?
    
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><p style="margin:0px 0px 0.25cm 0px;line-height:120%;">Yes, depending on your cloud client configuration.</p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;"><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style></p>
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


<p style="margin:0px 0px 0.25cm 0px;line-height:120%;">
	
	
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>


</p><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style><style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
		a:link { so-language: zxx }
	-->
	</style>
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "264.0",
    "currency": "EUR",
}