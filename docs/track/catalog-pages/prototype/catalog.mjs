// THROWAWAY: parses the publisher's mapping-only YAML subset, not arbitrary YAML.
// All unsigned integers remain decimal strings, including IDs and byte sizes.
export function parseCatalog(text) {
 const root=Object.create(null), stack=[{indent:-2,value:root}];
 const string=s=>JSON.parse(s.replace(/\\N/g,'\\u0085').replace(/\\L/g,'\\u2028').replace(/\\P/g,'\\u2029'));
 for(const line of text.trimEnd().split('\n')) {
  const m=/^( *)("(?:[^"\\]|\\.)*"|[a-z_]+):(?: (.*))?$/.exec(line);
  if(!m || m[1].length%2) throw Error('Outside supported catalog YAML subset');
  const indent=m[1].length,key=m[2][0]==='"'?string(m[2]):m[2],raw=m[3];
  while(stack.at(-1).indent>=indent) stack.pop();
  if(indent!==stack.at(-1).indent+2) throw Error('Invalid indentation');
  const parent=stack.at(-1).value;
  if(Object.hasOwn(parent,key)) throw Error('Duplicate key');
  let value;
  if(raw===undefined || raw==='{}') value=Object.create(null);
  else if(raw[0]==='"') value=string(raw);
  else if(raw==='true'||raw==='false') value=raw==='true';
  else if(/^(0|[1-9][0-9]*)$/.test(raw)) value=raw;
  else throw Error('Unsupported scalar');
  parent[key]=value;
  if(raw===undefined) stack.push({indent,value});
 }
 if(root.format!=='2') throw Error('Expected catalog format 2');
 return root;
}
export const rawURL=(pin,path)=>`https://raw.githubusercontent.com/mareklangiewicz/AM/${pin}/${path}`;
