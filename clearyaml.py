

# Take a model file called infile and clear all values from its YAML, leaving comments intact. Replace values with null.
def clearYAML(infile="content/wiki/_defaultYAML.md", outfile="", outPrint=True):
  with open( infile, 'r' ) as f:
    lines = f.readlines()  # each line includes \n at the end.
  res = []
  for line in lines:
    if line.startswith( "#" ):
      res += ["\n" + line]
      continue

    elif ":" in line:
      if line.startswith( " " ):
        res += [line[: line.index( ":" )] + ": null"]
      else:
        res += [line[: line.index( ":" ) + 1]]

  if outPrint:
    for line in res:
      print( line )

  if outfile:
    with open( outfile, "w" ) as f:
      f.write( res )

  return res


# Load YAML from a file into a dict to compare with a model for missing/updating keys.
# Result is dict key -> {hashtag, text, source, comment} or key -> {hashtag, value}
class d( dict ):
  def update(self, *args, **kwargs):
    super().update( *args, **kwargs )
    return self

  # Useful for return k-v pairs when dict only has 1 pair. Otherwise returns the first pair in the dict.
  def pair(self):
    for key in self:
      return key, self[key]


def parse_yaml(txt, null=None):
  # Returns dict parsing yaml string.
  parsedDict = d()
  if type( txt ) == type( list ):
    lines = txt
  else:
    lines = txt.split( "\n" )

  for line in lines:
    if not line:
      continue
    k, _, v = line.lstrip( "  " ).rstrip( "\n" ).partition( ": " )
    if not k.endswith( ":" ):
      k = k + ":"
    if v == "null":
      parsedDict[k] = null
    else:
      parsedDict[k] = v

  return parsedDict


def loadYAMLdefault(infile="content/wiki/_defaultYAML.md", null=None):
  with open( infile, "r" ) as f:
    lines = f.readlines()

  defaultYAML = dict()
  idx = 1  # The first line is always --- to please Hugo.

  while not lines[idx][:3] == "---":
    line = lines[idx]

    if line.startswith( "# " ):
      title = line.rstrip( "\n" )
      key = lines[idx + 1].rstrip( "\n" )
      if lines[idx + 2].startswith( "  text:" ):
        block = parse_yaml( "".join( lines[idx + 2:idx + 5] ) )
        defaultYAML[key] = d( title=title ).update( block )
        idx += 5
      else:
        key, v = parse_yaml( lines[idx + 1] ).pair()
        defaultYAML[key] = d( title=title, value=v )
        idx += 2

    elif line.startswith( "##" ):  # Used for Section titles
      key = line.rstrip( "\n" )
      defaultYAML[key] = "null"
      idx += 1

    # These values don't have titles in text, and look muddy in source if we add hashtags.
    elif any( line.startswith( x ) for x in ["title:", "name:", "symbol:", "tags:", "currency:"] ):
      defaultYAML.update( parse_yaml( line ) )
      idx += 1
    else:
      idx += 1

  return defaultYAML


def check_missing_YAML(coin, modelFile="content/wiki/_defaultYAML.md", modelDict=None):
  dir = f"content/wiki/"
  if modelDict:
    model = modelDict
  else:
    model = loadYAMLdefault( modelFile )

  if type( coin ) == str:
    if coin.startswith( "content" ):
      coinDict = loadYAMLdefault( coin )
    else:
      coinDict = loadYAMLdefault( f"content/wiki/{coin}.md" )

  for key in model:
    if key not in coinDict:
      print( f"Key: {key} not in {coin}" )

  pretty( coinDict )
  return


btc = loadYAMLdefault( "content/wiki/bitcoin.md" )
check_missing_YAML( "bitcoin" )


def coin():
  a = input( "Enter coin name" )
  return loadYAMLdefault( f"content/wiki/{a}.md" )
