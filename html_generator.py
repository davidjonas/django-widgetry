"""
Widgetry HTML page generator.
version = 1.0
"""
from django.template import Template as DjangoTemplate, RequestContext

class Widget(object):
    """
    BaseClass for renderable widgets
    """
    content = ""
    name = ""
    JS = []
    CSS = []
    resources=[]
    inlineJS = ""
    parent=None
    
    def add(self, html):
        """
        Add to content.
        """
        self.content = self.content + html
    
    def setParent(self, parent):
        """
        Sets the parent Page to add requisites on css and js files
        """
        self.parent=parent
        self._addPrerequisites()
    
    def requireJSFile(self, js, index=None, before=None, after=None):
        """
        Adds a requirement to a JS file, it will be added to the parent page
        """
        self.JS.append({'file':js, 'index':index, 'before':before, 'after':after})
        
    def requireCSSFile(self, css, index=None, before=None, after=None):
        """
        Adds a requirement to a CSS file, it will be added to the parent page
        """
        self.CSS.append({'file':css, 'index':index, 'before':before, 'after':after})
        
    def requireResourceFile(self, resource, index=None, before=None, after=None):
        """
        Adds a requirement to a resource file, it will be added to the parent page
        """
        self.resources.append({'file':resource, 'index':index, 'before':before, 'after':after})
    
    def requireInlineJS(self,js):
        """
        Includes inline JS into the page's head js is a string with javascript code to be included on the page.
        """
        self.inlineJS = self.inlineJS + '%s'%js
        
    def _addPrerequisites(self):
        if self.parent is not None:
            for cssFile in self.CSS:
                self.parent.addCSSFile(cssFile["file"], index=cssFile["index"], before=cssFile["before"], after=cssFile["after"])
            for jsFile in self.JS:
                self.parent.addJSFile(jsFile["file"], index=jsFile["index"], before=jsFile["before"], after=jsFile["after"])
            if self.inlineJS != "":
                self.parent.addInlineJS(self.inlineJS)
        
    def render(self):
        """
        render the html of the widget
        """
        return """
        <div class="widget">
            %(content)s
        </div>
        """%{"name":self.name, "content":self.content}

class Page(object):
    """
    Page class to render html. Can be used as is but should be subclassed to create a specific 'main template'
    and then subclass Template to add content to it.
    
    To render the page through the Django templating engine snd the request with the 
    """
    request = None
    render_as_template = True
    title = ""
    headDirectives = []
    JS = []
    CSS = []
    resources = []
    inlineJS = ""
    inlineCSS = ""
    content = ""
    googleAnalytics = ""

    
    def __init__(self, title, request=None, render_as_template=True):
        """
        Constructor
        """
        self.request = request
        self.render_as_template = render_as_template
        self.title = "<title>%s</title>"%title
        self.headDirectives = []
        self.JS = []
        self.CSS = []
        self.resources = []
        self.inlineJS = ""
        self.inlineCSS = ""
        self.content = ""
        self.googleAnalytics = ""
        self.doctype='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        
       
    @property
    def Body(self):
        """
        Renders the body of the page
        """
        return """
        <body>
            <div class="main_wrapper">
                %(content)s
            </div>
        </body>
        """%{"content": self.content}
        
        
    @property
    def Head(self):
        """
        renders the head of the page
        """
        return """
        <head>
            %(title)s
            %(headDirectives)s
            %(resources)s
            %(JS)s
            %(CSS)s
            %(inlineJS)s
            %(inlineCSS)s
        </head>
        """%{
            "title": self.title,
            "headDirectives": ''.join(self.headDirectives),
            "JS":''.join(self.JS),
            "CSS":''.join(self.CSS),
            "resources":''.join(self.resources),
            "inlineJS":self.inlineJS,
            "inlineCSS":self.inlineCSS
            }
    
    def add(self, html):
        """
        Append HTML content to the page 
        """
        self.content = self.content + html
        
    def addWidget(self, widget):
        widget.setParent(self)
        self.add(widget.render())
        
    def addCSSFile(self, css, index=None, before=None, after=None, media="all"):
        """
        Includes a CSS file on the page:
        * index: which order to include this file
        * before: include this file before an already included file (inserts in the end if [before] file does not exist)
        * after: include this file immediately after an already included file (throws ValueError if [after] file does not exist )
        """
        #TODO: add after="*" and before="*" like Plone
        #TODO: add media option without breaking the search, maybe store only the names and generate HTML in render time
        if '<link type="text/css" rel="stylesheet" href="%s" />'%css not in self.CSS:
            if before is not None:
                try:
                    index = self.CSS.index('<link type="text/css" rel="stylesheet" href="%s" />'%before)
                except ValueError:
                    index = None
                
            if after is not None:
                index = self.CSS.index('<link type="text/css" rel="stylesheet" href="%s" />'%after) + 1
                
            if index is None:
                self.CSS.append('<link type="text/css" rel="stylesheet" href="%s" />'%css)
            else:
                self.CSS.insert(index, '<link type="text/css" rel="stylesheet" href="%s" />'%css)
        
    def addJSFile(self, js, index=None, before=None, after=None):
        """
        Includes a JS file on the page:
        * index: which order to include this file
        * before: include this file before an already included file (inserts in the end if [before] file does not exist)
        * after: include this file immediately after an already included file (throws ValueError if [after] file does not exist )
        """
        if '<script type="text/javascript" src="%s"></script>'%js not in self.JS:
            if before is not None:
                try:
                    index = self.JS.index('<script type="text/javascript" src="%s"></script>'%before)
                except ValueError:
                    index = None
                
            if after is not None:
                index = self.JS.index('<script type="text/javascript" src="%s"></script>'%after) + 1
                
            if index is None:
                self.JS.append('<script type="text/javascript" src="%s"></script>'%js)
            else:
                self.JS.insert(index, '<script type="text/javascript" src="%s"></script>'%js)
                
    def addResourceFile(self, resource, index=None, before=None, after=None):
        """
        Includes a resource (link rel="resources") file on the page:
        * index: which order to include this file in
        * before: include this file before an already included file (inserts in the end if [before] file does not exist)
        * after: include this file immediately after an already included file (throws ValueError if [after] file does not exist )
        """
        if '<link rel="resources" href="%s" />'%resource not in self.resources:
            if before is not None:
                try:
                    index = self.resources.index('<link rel="resources" href="%s"  type="text/html" />'%before)
                except ValueError:
                    index = None
                
            if after is not None:
                index = self.resources.index('<link rel="resources" href="%s" type="text/html" />'%after) + 1
                
            if index is None:
                self.resources.append('<link rel="resources" href="%s" type="text/html" />'%resource)
            else:
                self.resources.insert(index, '<link rel="resources" href="%s" type="text/html" />'%resource)
        
    def addInlineJS(self,js):
        """
        Includes inline JS into the page's head js is a string with javascript code to be included on the page.
        """
        self.inlineJS = self.inlineJS + '<script type="text/javascript">%s</script>'%js
        
    def addInlineCSS(self,css):
        """
        Includes inline CSS into the page's head css is a string with css code to be included on the page.
        """
        self.inlineCSS = self.inlineCSS + '<style type="text/css">%s</style>'%css 
    
    def setDocType(self, doc):
        """
        Sets the doctype of the final render
        """
        self.doctype = doc
    
    def addHeadDirective(self, headDir):
        """
        Adds whatever code you send in to the head.
        """
        self.headDirectives.append(headDir)
        
    def render(self):
        """
        Render full HTML of the page. Use this to send as response to the client.
        """
        HTML = """
%(doctype)s
<html xmlns="http://www.w3.org/1999/xhtml">
    %(Head)s
    %(Body)s
    %(googleAnalytics)s
</html>
        """%{"Head":self.Head, "Body":self.Body, "googleAnalytics": self.googleAnalytics, "doctype":self.doctype}
        
        HTMLRender = ""
        
        if self.request is not None and self.render_as_template:
            djangoTemplate = DjangoTemplate(HTML)
            HTMLRender = djangoTemplate.render(RequestContext(self.request, {}))
        else:
            HTMLRender = HTML
        
        return HTMLRender
 
    
class Template(object):
    """
    Does the same as a Page but renders the raw content only (no head, body etc...) and adds JS and CSS to the parent page like a widget. This is great to create Page templates
    and add them to the "main page". You can render it just like a regular Page
    """
    parent=None
    content = ""
    
    def __init__(self, parent_page):
        """
        Does the same as a Page but renders and adds JS and CSS to the parent page like a widget. This is great to create Page templates
        and add them to the "main page"
        Requires a subclass of Page as parent
        """
        self.parent = parent_page
        self.content=""
        
    def add(self, html):
        """
        Append HTML content to the template 
        """
        self.content = self.content + html
    
    def addWidget(self, widget):
        """
        adds a widjet while adding the requirements to the parent Page
        """
        widget.setParent(self.parent)
        self.add(widget.render())
    
    def addJSFile(self, js, index=None, before=None, after=None):
        """
        Includes a JS file on the parent Page:
        * index: which order to include this file in
        * before: include this file before an already included file (inserts in the end if [before] file does not exist)
        * after: include this file immediately after an already included file (throws ValueError if [after] file does not exist )
        """
        self.parent.addJSFile(js, index=index, before=before, after=after)
    
    def addCSSFile(self, css, index=None, before=None, after=None):
        """
        Includes a CSS file on the parent Page:
        * index: which order to include this file in
        * before: include this file before an already included file (inserts in the end if [before] file does not exist)
        * after: include this file immediately after an already included file (throws ValueError if [after] file does not exist )
        """
        self.parent.addCSSFile(css, index=index, before=before, after=after)
        
    def addResourceFile(self, resource, index=None, before=None, after=None):
        """
        Includes a resource (link rel="resources") file on the parent Page:
        * index: which order to include this file in
        * before: include this file before an already included file (inserts in the end if [before] file does not exist)
        * after: include this file immediately after an already included file (throws ValueError if [after] file does not exist )
        """
        self.parent.addResourceFile(resource, index=index, before=before, after=after)
        
    def addInlineJS(self,js):
        """
        Includes inline JS into the parnet page's head js is a string with javascript code to be included on the page.
        """
        self.parent.addInlineJS(js)
    
    def addInlineCSS(self,css):
        """
        Includes inline CSS into the parent page's head js is a string with javascript code to be included on the page.
        """
        self.parent.addInlineCSS(css)
        
    def render(self):
        self.parent.add(self.content)
        return self.parent.render()
        
    
    