# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import werkzeug
import itertools
import pytz
import babel.dates
from collections import OrderedDict

from odoo import http, fields
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request
from odoo.osv import expression
from odoo.tools import html2plaintext

import logging
_logger = logging.getLogger(__name__)


class WebsiteInformation(http.Controller):
    _blog_post_per_page = 10
    _post_comment_per_page = 10

    def nav_list(self, blog=None):
        print("===============================24")
        dom = blog and [('blog_id', '=', blog.id)] or []
        if not request.env.user.has_group('website.group_website_designer'):
            dom += [('post_date', '<=', fields.Datetime.now())]
        groups = request.env['information.letter.post']._read_group_raw(
            dom,
            ['name', 'post_date'],
            groupby=["post_date"], orderby="post_date desc")
        for group in groups:
            (r, label) = group['post_date']
            start, end = r.split('/')
            group['post_date'] = label
            group['date_begin'] = start
            group['date_end'] = end

            locale = request.context.get('lang') or 'en_US'
            start = pytz.UTC.localize(fields.Datetime.from_string(start))
            tzinfo = pytz.timezone(request.context.get('tz', 'utc') or 'utc')

            group['month'] = babel.dates.format_datetime(start, format='MMMM', tzinfo=tzinfo, locale=locale)
            group['year'] = babel.dates.format_datetime(start, format='YYYY', tzinfo=tzinfo, locale=locale)

        return OrderedDict((year, [m for m in months]) for year, months in itertools.groupby(groups, lambda g: g['year']))

    @http.route([
        '/information_letter',
        '/information_letter/page/<int:page>',
    ], type='http', auth="public", website=True)
    def information_letters(self, page=1, **post):
        domain = request.website.website_domain()
        print("\n\n")
        _logger.info("information_letters domain :::::::::::: %s", domain)

        Blog = request.env['information.letter']
        blogs = Blog.search(domain, limit=2)
        _logger.info("information_letters blogs :::::::::::: %s", blogs)
        if len(blogs) == 1:
            _logger.info("Return information_letters ::::::::::::")
            return werkzeug.utils.redirect('/information_letter/%s' % slug(blogs[0]), code=302)

        InformationLetterPost = request.env['information.letter.post']
        total = InformationLetterPost.search_count(domain)

        pager = request.website.pager(
            url='/information_letter',
            total=total,
            page=page,
            step=self._blog_post_per_page,
        )
        posts = InformationLetterPost.search(domain, offset=(page - 1) * self._blog_post_per_page, limit=self._blog_post_per_page)
        blog_url = QueryURL('', ['blog', 'tag'])
        return request.render("ki_information_letter.latest_information_letter", {
            'posts': posts,
            'pager': pager,
            'blog_url': blog_url,
        })

    @http.route([
        '''/information_letter/<model("information.letter", "[('website_id', 'in', (False, current_website_id))]"):blog>''',
        '''/information_letter/<model("information.letter"):blog>/page/<int:page>''',
        '''/information_letter/<model("information.letter"):blog>/tag/<string:tag>''',
        '''/information_letter/<model("information.letter"):blog>/tag/<string:tag>/page/<int:page>''',
    ], type='http', auth="public", website=True)
    def information_letter(self, blog=None, tag=None, page=1, **opt):
        print("==========================84")
        """ Prepare all values to display the blog.

        :return dict values: values for the templates, containing

         - 'blog': current blog
         - 'blogs': all blogs for navigation
         - 'pager': pager of posts
         - 'active_tag_ids' :  list of active tag ids,
         - 'tags_list' : function to built the comma-separated tag list ids (for the url),
         - 'tags': all tags, for navigation
         - 'state_info': state of published/unpublished filter
         - 'nav_list': a dict [year][month] for archives navigation
         - 'date': date_begin optional parameter, used in archives navigation
         - 'blog_url': help object to create URLs
        """
        if not blog.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')
        published_count, unpublished_count = 0, 0

        domain = request.website.website_domain()

        InformationLetterPost = request.env['information.letter.post']

        Blog = request.env['information.letter']
        blogs = Blog.search(domain, order="create_date asc")

        # retrocompatibility to accept tag as slug
        active_tag_ids = tag and [int(unslug(t)[1]) for t in tag.split(',')] or []
        if active_tag_ids:
            fixed_tag_slug = ",".join(slug(t) for t in request.env['information.letter.tag'].browse(active_tag_ids).exists())
            if fixed_tag_slug != tag:
                new_url = request.httprequest.full_path.replace("/tag/%s" % tag, "/tag/%s" % fixed_tag_slug, 1)
                if new_url != request.httprequest.full_path:  # check that really replaced and avoid loop
                    return request.redirect(new_url, 301)
            domain += [('tag_ids', 'in', active_tag_ids)]
        if blog:
            domain += [('blog_id', '=', blog.id)]
        if date_begin and date_end:
            domain += [("post_date", ">=", date_begin), ("post_date", "<=", date_end)]

        if request.env.user.has_group('website.group_website_designer'):
            count_domain = domain + [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            published_count = InformationLetterPost.search_count(count_domain)
            unpublished_count = InformationLetterPost.search_count(domain) - published_count

            if state == "published":
                domain += [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            elif state == "unpublished":
                domain += ['|', ("website_published", "=", False), ("post_date", ">", fields.Datetime.now())]
        else:
            domain += [("post_date", "<=", fields.Datetime.now())]

        blog_url = QueryURL('', ['information_letter', 'tag'], blog=blog, tag=tag, date_begin=date_begin, date_end=date_end)

        blog_posts = InformationLetterPost.search(domain, order="id asc")
        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=len(blog_posts),
            page=page,
            step=self._blog_post_per_page,
            url_args=opt,
        )
        pager_begin = (page - 1) * self._blog_post_per_page
        pager_end = page * self._blog_post_per_page
        blog_posts = blog_posts[pager_begin:pager_end]

        all_tags = request.env['information.letter.tag']#blog.all_tags()[blog.id]

        # function to create the string list of tag ids, and toggle a given one.
        # used in the 'Tags Cloud' template.
        def tags_list(tag_ids, current_tag):
            print("=================================158")
            tag_ids = list([]) # required to avoid using the same list
            if current_tag in tag_ids:
                tag_ids.remove(current_tag)
            else:
                tag_ids.append(current_tag)
            tag_ids = request.env['information.letter.tag'].browse(tag_ids).exists()
            return ','.join(slug(tag) for tag in tag_ids)

        tag_category = sorted(all_tags.mapped('category_id'), key=lambda category: category.name.upper())
        other_tags = sorted(all_tags.filtered(lambda x: not x.category_id), key=lambda tag: tag.name.upper())

        values = {
            'blog': blog,
            'blogs': blogs,
            'main_object': blog,
            'other_tags': other_tags,
            'state_info': {"state": state, "published": published_count, "unpublished": unpublished_count},
            'active_tag_ids': active_tag_ids,
            'tags_list' : tags_list,
            'blog_posts': blog_posts,
            'blog_posts_cover_properties': [json.loads(b.cover_properties) for b in blog_posts],
            'pager': pager,
            'nav_list': self.nav_list(blog),
            'blog_url': blog_url,
            'date': date_begin,
            'tag_category': tag_category,
        }
        _logger.info("information_letters values :::::192::::::: %s", values)
        response = request.render("ki_information_letter.information_letter_post_short", values)
        return response

    @http.route([
            '''/information_letter/<model("information.letter", "[('website_id', 'in', (False, current_website_id))]"):blog>/post/<model("information.letter.post", "[('blog_id','=',blog[0])]"):blog_post>''',
    ], type='http', auth="public", website=True)
    def information_letter_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        """ Prepare all values to display the blog.

        :return dict values: values for the templates, containing

         - 'blog_post': browse of the current post
         - 'blog': browse of the current blog
         - 'blogs': list of browse records of blogs
         - 'tag': current tag, if tag_id in parameters
         - 'tags': all tags, for tag-based navigation
         - 'pager': a pager on the comments
         - 'nav_list': a dict [year][month] for archives navigation
         - 'next_post': next blog post, to direct the user towards the next interesting post
        """
        if not blog.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        InformationLetterPost = request.env['information.letter.post']
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        pager_url = "/blog/%s" % blog_post.id

        pager = request.website.pager(
            url=pager_url,
            total=len(blog_post.website_message_ids),
            page=page,
            step=self._post_comment_per_page,
            scope=7
        )
        pager_begin = (page - 1) * self._post_comment_per_page
        pager_end = page * self._post_comment_per_page
        comments = blog_post.website_message_ids[pager_begin:pager_end]

        tag = None
        if tag_id:
            tag = request.env['information.letter.tag'].browse(int(tag_id))
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog_post.blog_id, tag=tag, date_begin=date_begin, date_end=date_end)

        if not blog_post.blog_id.id == blog.id:
            return request.redirect("/information_letter/%s/post/%s" % (slug(blog_post.blog_id), slug(blog_post)), code=301)

        tags = request.env['information.letter.tag'].search([])

        # Find next Post
#         blog_post_domain = [('blog_id', '=', blog.id)]
        blog_post_domain = []

        if not request.env.user.has_group('website.group_website_designer'):
            blog_post_domain += [('post_date', '<=', fields.Datetime.now())]

        all_post = InformationLetterPost.search(blog_post_domain)
        print("all_post -------------------",all_post)

        if blog_post not in all_post:
            return request.redirect("/information_letter/%s" % (slug(blog_post.blog_id)))

        # should always return at least the current post
        all_post_ids = all_post.ids
        print("all_post_ids ---------------------",all_post_ids)
        current_blog_post_index = all_post_ids.index(blog_post.id)
        print("current_blog_post_index ---------",current_blog_post_index)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and InformationLetterPost.browse(next_post_id) or False
        print("next_post ---------------",next_post)

        prev_post_id = all_post_ids[(current_blog_post_index - 1) % nb_posts] if nb_posts > 1 else None
        prev_post = next_post_id and InformationLetterPost.browse(prev_post_id) or False

        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'blog_post': blog_post,
            'blog_post_cover_properties': json.loads(blog_post.cover_properties),
            'main_object': blog_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'prev_post': prev_post,
            'next_post_cover_properties': json.loads(next_post.cover_properties) if next_post else {},
            'date': date_begin,
            'blog_url': blog_url,
            'pager': pager,
            'comments': comments,
        }
        _logger.info("information_letter_post values :::::279::::::: %s", values)

        response = request.render("ki_information_letter.information_letter_post_complete", values)

        request.session[request.session.sid] = request.session.get(request.session.sid, [])
        if not (blog_post.id in request.session[request.session.sid]):
            request.session[request.session.sid].append(blog_post.id)
            # Increase counter
            blog_post.sudo().write({
                'visits': blog_post.visits+1,
                'write_date': blog_post.write_date,
            })
        return response

#     @http.route('/blog/<int:blog_id>/post/new', type='http', auth="public", website=True)
#     def information_letter_post_create(self, blog_id, **post):
#         print("============================296")
#         # Use sudo so this line prevents both editor and admin to access blog from another website
#         # as browse() will return the record even if forbidden by security rules but editor won't
#         # be able to access it
#         if not request.env['information.letter'].browse(blog_id).sudo().can_access_from_current_website():
#             raise werkzeug.exceptions.NotFound()
# 
#         new_blog_post = request.env['information.letter.post'].create({
#             'blog_id': blog_id,
#             'website_published': False,
#         })
#         return werkzeug.utils.redirect("/blog/%s/post/%s?enable_editor=1" % (slug(new_blog_post.blog_id), slug(new_blog_post)))

#     @http.route('/blog/post_duplicate', type='http', auth="public", website=True, methods=['POST'])
#     def information_letter_post_copy(self, blog_post_id, **post):
#         print("=============================311")
#         """ Duplicate a blog.
# 
#         :param blog_post_id: id of the blog post currently browsed.
# 
#         :return redirect to the new blog created
#         """
#         new_blog_post = request.env['information.letter.post'].with_context(mail_create_nosubscribe=True).browse(int(blog_post_id)).copy()
#         return werkzeug.utils.redirect("/blog/%s/post/%s?enable_editor=1" % (slug(new_blog_post.blog_id), slug(new_blog_post)))
# 
#     @http.route('/blog/post_change_background', type='json', auth="public", website=True)
#     def change_bg(self, post_id=0, cover_properties={}, **post):
#         print("================================323")
#         if not post_id:
#             return False
#         return request.env['information.letter.post'].browse(int(post_id)).write({'cover_properties': json.dumps(cover_properties)})
# 
#     @http.route(['/blog/render_latest_posts'], type='json', auth='public', website=True)
#     def render_latest_posts(self, template, domain, limit=None, order='published_date desc'):
#         print("==================================330")
#         dom = expression.AND([
#             [('website_published', '=', True), ('post_date', '<=', fields.Datetime.now())],
#             request.website.website_domain()
#         ])
#         if domain:
#             dom = expression.AND([dom, domain])
#         posts = request.env['information.letter.post'].search(dom, limit=limit, order=order)
#         return request.website.viewref(template).render({'posts': posts})
