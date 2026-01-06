import sys
sys.path.insert(0, 'src')
from new_crew.tools.serper_tool import SerperSearchTool

t = SerperSearchTool()
try:
    out = t._run('test query', 2)
    print('OUTPUT:', out)
except Exception as e:
    import traceback
    traceback.print_exc()
