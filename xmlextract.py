import os

from argparse import ArgumentParser
from datetime import datetime
from lxml import etree
import unicodedata

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def pathify(outdir, title, date):
    # Dates are in ISO: Mon, 03 Jan 2011 07:17:00 +0000
    dt = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
    dts = dt.strftime('%Y%m%d %H%M')
    t = strip_accents(title)
    t = t.encode('ascii', errors='ignore').decode('ascii').lower()
    t = t.translate(str.maketrans('', '', '''!"#¤%&/'()=?\.,;][{@£$€¥}:\n\t'''))

    count = 1
    filename = '%s %s.html' % (dts, t)
    while True:
        fullpath = os.path.join(outdir, filename)
        if not os.path.exists(fullpath):
            break
        count += 1
        filename = '%s %s-%s.html' % (dts, t, count)

    print(filename)
    return fullpath

def main():
    parser = ArgumentParser(description='Extraherar text från Jörgens XML')
    parser.add_argument('infile', type=str, help='Namnet på filen')
    parser.add_argument('outdir', type=str, help='Lägg filerna här')

    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    data = []
    tree = etree.parse(args.infile)
    nsmap = tree.xpath('/rss')[0].nsmap
    for tag in tree.xpath('/rss/channel/item'):
        data = {
            'title': tag.xpath('title')[0].text,
            'date': tag.xpath('pubDate')[0].text,
            'link': tag.xpath('link')[0].text,
            'creator': tag.xpath('dc:creator', namespaces=nsmap)[0].text,
            'excerpt': tag.xpath('excerpt:encoded', namespaces=nsmap)[0].text,
        }
        content = tag.xpath('content:encoded', namespaces=nsmap)[0].text
        path = pathify(args.outdir, data['title'], data['date'])
        with open(path, 'wt', encoding='utf8') as outfile:
            head = '<html><head><meta charset="UTF-8"/><title>{title}</title></head>\n'.format(**data)
            title = '<body><h1>{title}</h1><p>{excerpt}</p>\n'.format(**data)
            lead = '<p>{date}, {creator}<br/>{link}</p>\n'.format(**data)
            foot = '\n</body></html>'.format(**data)

            outfile.write(head)
            outfile.write(title)
            outfile.write(lead)
            outfile.write(content)
            outfile.write(foot)


if __name__ == "__main__":
    main()


