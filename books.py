#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

"""
Script for parsing book recommendations from Back to Work's feed.

This  script fetches shownotes of Back to Work, a podcast, and parses the
different book recommendations made on the show.
"""

import codecs
from datetime import datetime
import feedparser
import sys
import re

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

authors = {
    'Christopher Eliopoulos': 'Christopher Eliopoulos',
    'So Good They Can\'t Ignore You: Why Skills Trump Passion in the Quest ' +
    'for Work You Love': 'Cal Newport',
    'Secret War Brian Michael Bendis, Gabriele Dell Otto':
        'Brian Michael Bendis, Gabriele Dell Otto',
    'On Writing: 10th Anniversary Edition: A Memoir of the Craft':
        'Stephen King',
    'The Creative Habit: Learn It and Use It for Life':
        'Twyla Tharp, Mark Reiter',
    'A Confederacy of Dunces': 'John Kennedy Toole, Walker Percy',
    'A Kick in the Seat of the Pants: Using Your Explorer, Artist, Judge, ' +
        'and Warrior to Be More Creative': 'Roger Von Oech',
    'Mindfulness in Plain English': 'Bhante Henepola Gunaratana',
    'Getting Things Done: The Art of Stress-Free Productivity': 'David Allen',
    'Getting Things Done': 'David Allen',
    'Wherever You Go, There You Are: Mindfulness Meditation in Everyday Life' +
        ' [&quot;...book with brown and green cover...&quot;]':
        'Jon Kabat-Zinn',
    'The Waste Land: A Facsimile and Transcript of the Original Drafts ' +
        'Including the Annotations of Ezra Pound': 'T. S. Eliot',
    'The Man Who Couldn\'t Stop: OCD and the True Story of a Life Lost in ' +
        'Thought': 'David Adam',
    'The Adventure Time Encyclopaedia (Encyclopedia): Inhabitants, Lore, ' +
        'Spells, and Ancient Crypt Warnings of the Land of Ooo Circa 19.56 ' +
        'B.G.E. - 501 A.G.E.': 'Martin Olson'
}


def parse_books():
    """Function for parsing feed and gathering links."""
    url = 'http://feeds.5by5.tv/b2w'
    # filename = './b2w.xml'

    pattern = '<a[^>]* href="(https?:\/\/www\.amazon\.com[^"]*).*?>(.*?)</a>\
(?:</h4>\s*?(?:<p>(.*?)</p>))?'
    pattern2 = '<a[^>]*? href="((?!http:\/\/www\.amazon)[^"]*?)"[^>]*?>\
((?:Audio)?Book: .*?)</a>'
    skip = ['Health &amp; Personal Care', 'Toys &amp; Games', 'MP3 Downloads',
            'Computers &amp; Accessories', 'Musical Instruments', 'Moleskine',
            'Everything Else', 'Music', 'Electronics', 'Movies &amp; TV',
            'Sports &amp; Outdoors', 'Grocery &amp; Gourmet Food', ': Baby',
            'Amazon Instant Video', 'Kitchen &amp; Dining', 'Floor Lamp',
            'Wishlist', 'The Aviator', 'Home Improvement', 'Video Games',
            'Fingernail Clipper', 'Edimax N150 Wireless', 'Automotive',
            'ASUS Dual-Band Wireless', 'Camera &amp; Photo', 'Beauty',
            'Office Products', 'Crafts & Sewing', 'Patio, Lawn &amp; Garden',
            'Home &amp; Kitchen', 'Brass No Soliciting Sign', 'Light Bulb',
            'Ultra Pro Resealable Current Size Comic Bags', 'Model Rocket Kit',
            'Arts, Crafts &amp; Sewing', 'Colored Pencils', 'Wish List',
            'Clothing', 'Pasta Bowls', 'Prime Pantry', 'Kum AS2',
            'Amazon Echo', 'Echo Dot', 'Hepa Filter Air Purifiers',
            'Pencil Set', 'Cell Phones &amp; Accessories', 'Online Backup',
            'Home & Theater', 'Home Audio &amp; Theater', 'Alexa on Fire TV',
            'Philips Hue', 'Amazon Launchpad', 'Rocketbook Wave', 'Launchpad',
            'Gaffer Tape']
    regex = re.compile(pattern, re.IGNORECASE)
    regex2 = re.compile(pattern2, re.IGNORECASE)
    books = []

    feed = feedparser.parse(url)
    # feed = feedparser.parse(filename)

    for episode in feed.entries:
        links = regex.findall(episode.content[0].value)
        non_amazon = regex2.findall(episode.content[0].value)
        links += non_amazon

        for link in links:
            # skip items that are not really books
            for category in skip:
                if category in link[1]:
                    break
                # sheesh
                if 'Philips' in link[1] and 'Hue' in link[1]:
                    break
            else:
                # include episode info
                link += (episode.link, episode.title)

                # no duplicates
                if link not in books:
                    books.append(link)
    return books


def produce_list(books):
    """
    Function taking a list of books, and producing two HTML tables of books.

    The function alsow writes the HTML to a file using a template (index.tmpl).
    """
    filename = './index.tmpl'
    comics = ['Marvel Famous Firsts', 'Marvel Now', 'Thor:', 'X-Men',
              'Hawkeye', 'American Vampire', 'The Walking Dead', 'Watchmen',
              'X-Force', 'Daredevil', 'Spider-Man', 'Scarlet', 'She-Hulk',
              'Fantastic Four', 'Wolverine', 'Fiona Staples', 'Civil War',
              'Brian Michael Bendis', 'Marvels', 'Batman', 'Deadpool',
              'Avengers', 'Animal Man', 'Transmetropolitan', 'Volume 1',
              'Y: The Last Man', 'Zita the Spacegirl', 'Invincible:',
              '5 Ronin', 'Runaways', 'The Immortal Iron Fist', 'Superman',
              'The Wonderful Wizard of Oz', 'World War Hulk',
              'Incredible Hulk', 'Infinity Gauntlet', 'Punk Rock Jesus',
              'Black Science', 'Sex Criminals', 'Scott Pilgrim', 'BONE',
              'Hilo', 'Amulet']

    booklist = comiclist = ''
    bookcount = comiccount = authorcount = gtd = desccount = 0

    # sanitize book titles and extract book authors
    filteredbooks = filter_books(books)

    # group books by their name. This is used for mention count
    groups = group_books(filteredbooks)

    for i, book in enumerate(filteredbooks):
        (link, originaltitle, title, desc, author, episodeLink,
            episodeTitle) = book

        # parse episode number for sorting
        episode = episodeTitle[:episodeTitle.find(':')]
        titlevalue = re.sub(r'^(a|an|the)\s', '', title.lower())
        titlevalue = re.sub(r'[^a-z]', '', titlevalue)[:20]

        # include book description if it exists
        if desc and not re.search(r'sponsored by', desc, re.IGNORECASE):
            row = '<tr><td class="desc" title="Click for description"\
                  data-value="%s"><a href="%s">%s</a> &hellip;'\
                  % (titlevalue, link, title)
            row += '<p id="desc-%d" class="description" style="display: none">\
                   %s</p></td>' % (i, desc)
            desccount += 1
        else:
            row = '<tr><td data-value="%s"><a href="%s">%s</a></td>'\
                  % (titlevalue, link, title)

        author_value = get_author_value(author)

        # author and episode information
        row += '<td class="author" data-value="%s">%s</td>\
                <td data-value="%s"><a href="%s">%s</a></td>'\
                % (author_value, author, episode, episodeLink, episodeTitle)

        # compute occurences + identifying value to group by occurence, title
        key = re.sub(r'\s{2,}', ' ', title)
        key = re.sub(r', Vol\.', ' Vol.', key)
        key = re.sub(r'\:\s+', ':', key)[:18]
        val = groups[key] + ord(key[:1]) * 0.01 + ord(key[4:5]) * 0.001
        if len(key) > 10:
            val += ord(key[10:11]) * 0.001
        row += '<td class="mentions" data-value="%f">%d</td>\n</tr>\n'\
               % (val, groups[key] + 1)

        # comics go to their own list
        iscomic = False
        for comic in comics:
            if comic in originaltitle:
                iscomic = True
                break

        if iscomic:
            comiclist += row
            comiccount += 1
        else:
            booklist += row
            bookcount += 1
        if author != '':
            authorcount += 1
        if 'Getting Things Done' in title:
            gtd += 1

    # Write list to index.html
    with codecs.open(filename, 'r', 'utf-8') as template:
        html = template.read()
        html = html.replace('{tablebody}', booklist)
        html = html.replace('{bookcount}', str(bookcount))
        html = html.replace('{comicbody}', comiclist)
        html = html.replace('{comiccount}', str(comiccount))
        html = html.replace('{date}', "{:%Y-%m-%d}".format(datetime.now()))
        html = html.replace('{gtd}', str(gtd))

    if not html:
        print 'reading template from %s failed' % filename
        return

    with codecs.open(filename.replace('tmpl', 'html'), 'w', 'utf-8') as file:
        file.write(html)

    return (bookcount, comiccount, authorcount, desccount)


def get_author(title):
    """
    Parse author name(s) from book title.

    Usually book title contains the authors separated by a colon, for example
    "The Road: Cormac McCarthy". In some cases the colon is not followed by
    authors, for example: "Super Graphic: A Visual Guide to the Comic Book
    Universe". Therefore we need to guess if the string contains names or not.
    (By counting commas :)
    """
    # split title into title and author. Usually separated by ':'.
    if title.count(':') == title.count(' - ') and title.count(':') > 0:
        parts = title.split(' - ')
    elif ':' in title:
        parts = title.split(':')
    elif ' by ' in title:
        parts = title.split(' by ')
    else:
        parts = title.split(' - ')

    # remove empty parts
    parts = filter(lambda title: title.strip(': '), parts)

    # take last part of title
    author = parts.pop()

    if len(parts) >= 1:
        author = author.replace(' and ', ', ').replace(',,', ',')\
            .replace(' CZT', '').replace(' (ed.)', '')

        # remove middle name initials for easier heuristics about name
        simpleauthor = re.sub(r'\s[A-Z]\.', '', author)
        simpleauthor = simpleauthor.replace(' MSPT', '').strip()

        authorparts = len(simpleauthor.split(' '))
        commas = simpleauthor.count(',')

        # try to guess if string is either a list of authors or just part of
        # the title.
        # example: Andrew Hunt, David Thomas -> 4 names <= (1 comma + 1) * 2
        if authorparts > 3 and authorparts > (commas + 1) * 2 + 1:
            author = ''
        # more than three words without commas
        elif authorparts > 3 and commas == 0:
            author = ''
        # names don't contain numbers
        elif re.search(r'\d', author):
            author = ''

        if author != '':
            title = ': '.join(parts)
    else:
        author = ''

    # cleanup: remove whitespace and quotes around title
    title = re.sub(r'^\s?&quot;(.*)&quot;\s?$', r'\1', title)
    title = title.strip(' :,')

    if author == '' and title in authors:
        author = authors[title]

    # change "Author,Author" to "Author, Author"
    author = re.sub(r',([^\s])', r', \1', author)

    return (author, title)


def get_author_value(author):
    """Function converting an author name to a data-value used for sorting."""
    if author == '':
        return ''
    parts = author.split(',')
    author = parts[0].strip(' ')
    parts = author.split(' ')
    author = parts[-1]
    return author


def group_books(books):
    """
    Group books by their title.

    Take a substring of the title to match titles like these:
    "Writing Down the Bones: Freeing the Writer Within (Shambhala Library)"
    "Writing Down the Bones eBook"
    "Writing Down the Bones"

    Not working?
    Wreck This Journal (Black) Expanded Ed.
    Wreck This Journal

    The Creative Habit
    The Creative Habit:  Learn It and Use It for Life

    Not the same:
    A Writer's Coach: The Complete Guide to Writing Strategies That Work
    A Writer's Coach: An Editor's Guide to Words That Work
    """
    groups = {}
    for book in books:
        key = re.sub(r'\s{2,}', ' ', book[2])
        key = re.sub(r', Vol\.', ' Vol.', key)
        key = re.sub(r':\s+', ':', key)[:18]
        try:
            groups[key] += 1
        except KeyError:
            groups[key] = 0
    return groups


def filter_books(books):
    """
    Function for clearing book titles of non-title elements.

    Take a book title like "Born Standing Up: A Comic's Life: Steve Martin:
        9781416553656: Amazon.com: Books"
    ...and return title: Born Standing Up: A Comic's Life, author: Steve Martin
    """
    filteredwords = [';Book: ', 'BOOK: ', ': Books', ':Books', '[Amazon]',
                     'MDM: ', 'Amazon.com: Boo', 'Amazon: ', 'Amazon.com: ',
                     ': Amazon.com', ' at Amazon.com', ':Amazon', '(Amazon)',
                     '(Amazon.com)', ': Explore similar items',
                     ' - Amazon.com', 'Kindle Store', 'eBook', ' Audio',
                     ' (HIGHLY recommended by Merlin)', '<em>', '</em>']
    filteredbooks = []
    temp_books = []
    for i, book in enumerate(books):
        desc = False
        if len(book) == 5:
            link, title, desc, episodeLink, episodeTitle = book
        else:
            link, title, episodeLink, episodeTitle = book
        originaltitle = title

        # remove (9123912392925) from title
        title = re.sub(r'\(?[0-9]{6,}\)?', '', title)

        # filter out "Amazon.com" and similar things from the title
        for word in filteredwords:
            title = title.replace(word, '')
        title = re.sub(r'^(Audiobook|Book):', '', title)
        title = title.replace('&#x27;', '\'')

        # GTD with other names
        title = re.sub(r'^Getting Things Done$',
                       'Getting Things Done: The Art of Stress-Free ' +
                       'Productivity', title)
        if title == 'pick up your own copy of GTD':
            title = 'Getting Things Done: The Art of Stress-Free Productivity'

        # one stupid link in ep 72
        if title == 'Amazon':
            title = 'The Now Habit: A Strategic Program for Overcoming\
                     Procrastination and Enjoying Guilt-Free Play: \
                     Neil Fiore'

        # ep 15
        if title[:13] == 'Alan Watts - ':
            title = title[13:] + ' - Alan Watts'

        # try to guess author from title
        (author, title) = get_author(title)

        filteredbook = (link, originaltitle, title, desc, author, episodeLink,
                        episodeTitle)
        temp_book = (link, re.sub(r'\s{2,}', ' ', title), desc, author.strip(),
                     episodeLink, episodeTitle)

        if temp_book not in temp_books:
            filteredbooks.append(filteredbook)
            temp_books.append(temp_book)
    return filteredbooks

# run
books = parse_books()
count = produce_list(books)
print "found %d books and %d comics. %d authors and %d descriptions found."\
    % count
