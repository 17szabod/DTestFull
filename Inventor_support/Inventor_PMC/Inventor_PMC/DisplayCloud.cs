using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using Inventor;

namespace Inventor_PMC
{
    class DisplayCloud
    {
        static void Main(string[] args)
        {
            string filename = @"C:\Users\kisac\CLionProjects\DTestFull\data\black arrow.ipt";
            string shared_file = @"C:\Users\kisac\Downloads\nose_inv_spheres.txt";
            Application _invApp;
            try
            {
                _invApp = (Application)Marshal.GetActiveObject("Inventor.Application");
            }
            catch (Exception ex)
            {
                try
                {
                    Type invAppType = Type.GetTypeFromProgID("Inventor.Application");
                    _invApp = (Application)Activator.CreateInstance(invAppType);
                    _invApp.Visible = true;

                }
                catch (Exception ex2)
                {
                    Console.WriteLine(ex2.ToString());
                    Console.WriteLine("Unable to get or start Inventor");
                    return;
                }
            }

            //PartDocument doc = (PartDocument)_invApp.ActiveDocument;
            PartDocument doc = (PartDocument)_invApp.Documents.Open(filename);
            PartComponentDefinition cdef = (PartComponentDefinition)doc.ComponentDefinition;
            Sketch3D insketch = cdef.Sketches3D.Add();
            Sketch3D onsketch = cdef.Sketches3D.Add();
            Sketch3D outsketch = cdef.Sketches3D.Add();
            
            string txt = System.IO.File.ReadAllText(shared_file);
            string[] points = txt.Split('~');
            foreach (string point in points)
            {
                string[] tmp = point.Split('$');
                int pmc = int.Parse(tmp[0]);
                double[] parr = Array.ConvertAll(tmp[1].Substring(1, tmp[1].Length - 2).Replace(" ", "").Split(','), Double.Parse);
                Point p = _invApp.TransientGeometry.CreatePoint(parr[0]/10, parr[1]/10, parr[2]/10);
                if (pmc == 1)
                {
                    insketch.SketchPoints3D.Add(p);
                }
                else if (pmc == 0)
                {
                    onsketch.SketchPoints3D.Add(p);
                }
                else if (pmc == -1)
                {
                    outsketch.SketchPoints3D.Add(p);
                }
            }
            var blue = _invApp.TransientObjects.CreateColor(0, 0, 255);
            var red = _invApp.TransientObjects.CreateColor(255, 0, 0);
            var green = _invApp.TransientObjects.CreateColor(0, 255, 255);

            insketch.OverrideColor = green;
            onsketch.OverrideColor = red;
            outsketch.OverrideColor = blue;
            return;
        }
    }
}
