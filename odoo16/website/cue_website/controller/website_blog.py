# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import http, models, fields, tools, _
import werkzeug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug, slugify, _guess_mimetype
from odoo.tools import OrderedSet, escape_psql, html_escape as escape
from odoo.tools import sql
import logging

_logger = logging.getLogger(__name__)

class QueryURLBlock(object):
    def __init__(self, path='', path_args=None, **args):
        self.path = path
        self.args = args
        self.path_args = OrderedSet(path_args or [])

    def __call__(self, path=None, path_args=None, **kw):
        path = path or self.path
        for key, value in self.args.items():
            kw.setdefault(key, value)
        path_args = OrderedSet(path_args or []) | self.path_args
        paths, fragments = {}, []
        for key, value in kw.items():
            if value and key in path_args:
                if isinstance(value, models.BaseModel):
                    paths[key] = value.url_category or slug(value)
                else:
                    paths[key] = u"%s" % value
            elif value:
                if isinstance(value, list) or isinstance(value, set):
                    fragments.append(werkzeug.urls.url_encode([(key, item) for item in value]))
                else:
                    fragments.append(werkzeug.urls.url_encode([(key, value)]))
        for key in path_args:
            value = paths.get(key)
            if value is not None:
                path += '/' + key + '/' + value
        if fragments:
            path += '?' + '&'.join(fragments)
        return path


class CueWebsiteBlog(WebsiteBlog):

    @http.route([
        '/blog',
        '/blog/page/<int:page>',
        '/blog/tag/<string:tag>',
        '/blog/tag/<string:tag>/page/<int:page>',
        '''/blog/<string:blog>''',
        '''/blog/<string:blog>/page/<int:page>''',
        '''/blog/<string:blog>/tag/<string:tag>''',
        '''/blog/<string:blog>/tag/<string:tag>/page/<int:page>''',
    ], type='http', auth="public", website=True, sitemap=True)
    def blog(self, blog=None, tag=None, page=1, search=None, **opt):
        _logger.info('62 ...........')

        Blog = request.env['blog.blog']
        if blog:
            blog = Blog.search([('url_category','=', blog)])
            if not blog:
                return request.redirect('/blog')
        # TODO adapt in master. This is a fix for templates wrongly using the
        # 'blog_url' QueryURL which is defined below. Indeed, in the case where
        # we are rendering a blog page where no specific blog is selected we
        # define(d) that as `QueryURL('/blog', ['tag'], ...)` but then some
        # parts of the template used it like this: `blog_url(blog=XXX)` thus
        # generating an URL like "/blog?blog=blog.blog(2,)". Adding "blog" to
        # the list of params would not be right as would create "/blog/blog/2"
        # which is still wrong as we want "/blog/2". And of course the "/blog"
        # prefix in the QueryURL definition is needed in case we only specify a
        # tag via `blog_url(tab=X)` (we expect /blog/tag/X). Patching QueryURL
        # or making blog_url a custom function instead of a QueryURL instance
        # could be a solution but it was judged not stable enough. We'll do that
        # in master. Here we only support "/blog?blog=blog.blog(2,)" URLs.
        if isinstance(blog, str):
            blog = Blog.browse(int(re.search(r'\d+', blog)[0]))
            if not blog.exists():
                raise werkzeug.exceptions.NotFound()

        blogs = tools.lazy(lambda: Blog.search(request.website.website_domain(), order="create_date asc, id asc"))

        if not blog and len(blogs) == 1:
            url = QueryURLBlock('/blog/%s' % slug(blogs[0]), search=search, **opt)()
            return request.redirect(url, code=302)

        date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')

        if tag and request.httprequest.method == 'GET':
            # redirect get tag-1,tag-2 -> get tag-1
            tags = tag.split(',')
            if len(tags) > 1:
                url = QueryURLBlock('' if blog else '/blog', ['blog', 'tag'], blog=blog, tag=tags[0], date_begin=date_begin, date_end=date_end, search=search)()
                return request.redirect(url, code=302)

        values = self._prepare_blog_values(blogs=blogs, blog=blog, date_begin=date_begin, date_end=date_end, tags=tag, state=state, page=page, search=search)

        # in case of a redirection need by `_prepare_blog_values` we follow it
        if isinstance(values, werkzeug.wrappers.Response):
            return values

        if blog:
            values['main_object'] = blog
            values['blog_url'] = QueryURLBlock('', ['blog', 'tag'], blog=blog, tag=tag, date_begin=date_begin, date_end=date_end, search=search)
        else:
            values['blog_url'] = QueryURLBlock('/blog', ['tag'], date_begin=date_begin, date_end=date_end, search=search)

        return request.render("website_blog.blog_post_short", values)

    @http.route([
        '''/blog/<string:blog>/<string:blog_post>''',
    ], type='http', auth="public", website=True, sitemap=True)
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
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
        BlogBlog = request.env['blog.blog']
        _logger.info('129 ...........%s' %(blog))

        blog = BlogBlog.search([('url_category','=', blog)])
        _logger.info('130 ...........%s' %(blog))


        BlogPost = request.env['blog.post']
        blog_post = BlogPost.search([('url_name','=', blog_post)])
        _logger.info('135 ...........%s' %(blog_post))

        if not blog_post and not blog:
            return request.redirect('/')
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        domain = request.website.website_domain()
        blogs = blog.search(domain, order="create_date, id asc")

        tag = None
        if tag_id:
            tag = request.env['blog.tag'].browse(int(tag_id))
        blog_url = QueryURLBlock('', ['blog', 'tag'], blog=blog_post.blog_id, tag=tag, date_begin=date_begin, date_end=date_end)
        if not blog_post.blog_id.id == blog.id:
            return request.redirect("/blog/%s/%s" % (blog_post.blog_id.url_category, blog_post.url_name), code=301)

        tags = request.env['blog.tag'].search([])

        # Find next Post
        blog_post_domain = [('blog_id', '=', blog.id)]
        if not request.env.user.has_group('website.group_website_designer'):
            blog_post_domain += [('post_date', '<=', fields.Datetime.now())]

        all_post = BlogPost.search(blog_post_domain)

        if blog_post not in all_post:
            return request.redirect("/blog/%s" % (slug(blog_post.blog_id)))

        # should always return at least the current post
        all_post_ids = all_post.ids
        current_blog_post_index = all_post_ids.index(blog_post.id)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and BlogPost.browse(next_post_id) or False

        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'blog_post': blog_post,
            'blogs': blogs,
            'main_object': blog_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'date': date_begin,
            'blog_url': blog_url,
        }
        response = request.render("website_blog.blog_post_complete", values)

        if blog_post.id not in request.session.get('posts_viewed', []):
            if sql.increment_fields_skiplock(blog_post, 'visits'):
                if not request.session.get('posts_viewed'):
                    request.session['posts_viewed'] = []
                request.session['posts_viewed'].append(blog_post.id)
                request.session.touch()
        return response
