using System;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;
using SolidWorks.Interop.swdocumentmgr;
using System.Runtime.InteropServices;

namespace SW_PMC_Grid
{
    class Console_PMC
    {
        public static T Min<T>(params T[] values)
        {
            return values.Min();
        }

        public static T Max<T>(params T[] values)
        {
            return values.Max();
        }

        // args are of the form --SW_PMC_Grid.exe filepath density alg_tol-- where alg_tol is an optional argument
        static void Main(string[] args)
        {
            int density = int.Parse(args[1]);
            string filename = args[0];
            double pmc_param = double.Parse(args[2]);
            Console.WriteLine($"Running SolidWorks PMC with parameters pmc_param: {pmc_param}, density: {density}");
            double sys_eps = 1e-5;

            var progId = "SldWorks.Application";

            var progType = System.Type.GetTypeFromProgID(progId);

            var swApp = System.Activator.CreateInstance(progType) as SolidWorks.Interop.sldworks.ISldWorks;


            ModelDoc2 swModel = default(ModelDoc2);
            SketchManager swSkMgr = default(SketchManager);
            ModelDocExtension swModelDocExt = default(ModelDocExtension);
            Measure swMeasure = default(Measure);
            bool status = false;
            int errors = 0;
            int warnings = 0;
            string fileName = null;

            fileName = @filename;
            swModel = (ModelDoc2)swApp.OpenDoc6(fileName, (int)swDocumentTypes_e.swDocPART, (int)swOpenDocOptions_e.swOpenDocOptions_ReadOnly, "", ref errors, ref warnings);
            //Debug.Print(swModel.);
            //swApp.ActivateDoc3(swModel.GetTitle(), false, (int)swRebuildOnActivation_e.swRebuildActiveDoc, 0);
            swModel.SetReadOnlyState(true);
            swApp.GetUserPreferenceToggle((int)swUserPreferenceToggle_e.swExtRefNoPromptOrSave);

            swModelDocExt = (ModelDocExtension)swModel.Extension;

            swSkMgr = swModel.SketchManager;

            // Check whether document is active
            if (swModel == null)
            {
                swApp.SendMsgToUser2("A part document must be active.", (int)swMessageBoxIcon_e.swMbWarning, (int)swMessageBoxBtn_e.swMbOk);
                return;
            }

            // Check whether document is a part
            int modelType = 0;
            modelType = swModel.GetType();

            if (modelType != (int)swDocumentTypes_e.swDocPART)
            {
                swApp.SendMsgToUser2("A part document must be active.", (int)swMessageBoxIcon_e.swMbWarning, (int)swMessageBoxBtn_e.swMbOk);
                return;
            }

            PartDoc swPart = (PartDoc)swModel;
            Object[] bodies;
            Body2 swBody = null;
            bodies = (Object[])swPart.GetBodies2((int)swBodyType_e.swAllBodies, false);

            if (bodies == null)
            {
                Debug.Print($"Failed to find a body in document {swModel.GetTitle()}.");
                return;
            }

            for (int i= 0; i < bodies.Length; i++)
            {
                swBody = (Body2)bodies[i];
                Debug.Print("My body name is: " + swBody.Name);
            }
            if (bodies.Length == 1)
            {
                swBody = (Body2)bodies[0];
            } else
            {
                Debug.Print("Failed to find body to test.");
                return;
            }
            double[] bbox;
            bbox = (double[])swBody.GetBodyBox();
            double minX = Double.MaxValue;
            double minY = Double.MaxValue;
            double minZ = Double.MaxValue;
            double maxX = Double.MinValue;
            double maxY = Double.MinValue;
            double maxZ = Double.MinValue;
            /////////////////////////////////////////////////////
            // Need to more carefully get the bounding box:
            foreach (Face face in swBody.GetFaces())
            {
                var tessTriangles = face.GetTessTriangles(true);
                for (int i=0; i<tessTriangles.Length/9; i+=9)
                {
                    maxX = Max(tessTriangles[9 * i + 0], tessTriangles[9 * i + 3], tessTriangles[9 * i + 6], maxX);
                    minX = Min(tessTriangles[9 * i + 0], tessTriangles[9 * i + 3], tessTriangles[9 * i + 6], minX);
                    maxY = Max(tessTriangles[9 * i + 1], tessTriangles[9 * i + 4], tessTriangles[9 * i + 7], maxY);
                    minY = Min(tessTriangles[9 * i + 1], tessTriangles[9 * i + 4], tessTriangles[9 * i + 7], minY);
                    maxZ = Max(tessTriangles[9 * i + 2], tessTriangles[9 * i + 5], tessTriangles[9 * i + 8], maxZ);
                    minZ = Min(tessTriangles[9 * i + 2], tessTriangles[9 * i + 5], tessTriangles[9 * i + 8], minZ);
                }
            }
            /////////////////////////////////////////////////////
            //pmc_param = manual_pmc_param ? Math.Sqrt(xh * xh + yh * yh + zh * zh)/2 + sys_eps : double.Parse(args[2]);  // The minimum radius to not have holes plus sys_eps
            pmc_param /= 1000;
            // Now that we have computed an approximate, expand the grid
            minX -= pmc_param;
            minY -= pmc_param;
            minZ -= pmc_param;
            maxX += pmc_param;
            maxY += pmc_param;
            maxZ += pmc_param;
            double xh = (maxX - minX) / density;
            double yh = (maxY - minY) / density;
            double zh = (maxZ - minZ) / density;
            Console.WriteLine($"Bounding Box: {minX}, {minY}, {minZ}, {maxX}, {maxY}, {maxZ}");
            Console.WriteLine($"xh: {xh}, yh: {yh}, zh: {zh}");
            Console.WriteLine($"I am currently using pmc param of {pmc_param}, when the exact would be {Math.Sqrt(xh * xh + yh * yh + zh * zh) / 2 + sys_eps}");
            int[,,] pmc_results = new int[density + 1, density + 1, density + 1];

            double x, y, z;
            int count = 0;
            string out_string = "";  // out_string follows a format used by Rhino previously
            for (int a = 0; a <= density; a++)
            {
                x = minX + xh * a;
                for (int b = 0; b <= density; b++)
                {
                    y = minY + yh * b;
                    for (int c = 0; c <= density; c++)
                    {
                        count++;
                        z = minZ + zh * c;
                        if (count%(density*density) == 0)
                        {
                            Console.WriteLine($"Working on point ({x}, {y}, {z})");
                        }
                        pmc_results[a, b, c] = PMC(x, y, z, swBody, pmc_param, swModel, swModelDocExt);
                        out_string += $"~{pmc_results[a, b, c]}$({1000*x}, {1000*y}, {1000*z})";  // Need to convert back to mm
                    }
                }
            }

            status = swApp.CloseAllDocuments(true);
            if (!status)
            {
                Debug.Print("Failed to close documents");
                return;
            }

            swApp.ExitApp();

            // Write pmc results to a shared file
            System.IO.File.WriteAllText(@"C:\Users\danis\Coding\DTestFull\temp_SW_spheres.txt", out_string.Substring(1));

            return;
        }

        // Performs Point Membership Check on given model part swBody. Returns -1 for out, 0 for on, 1 for out, and -2 for failure.
        public static int PMC(double x, double y, double z, IBody2 swBody, double algorithm_parameter, ModelDoc2 swModel, ModelDocExtension swModelDocExt)
        {
            bool status;
            SketchManager swSkMgr = swModel.SketchManager;
            Measure swMeasure = default(Measure);
            swModel.ClearSelection();

            // Insert a new point
            swSkMgr.Insert3DSketch(true);
            SketchPoint skPoint = default(SketchPoint);
            skPoint = swSkMgr.CreatePoint(x, y, z);
            swSkMgr.InsertSketch(true);

            if (skPoint == null)
            {
                Debug.Print("Failed to create point.");
                Console.WriteLine("Failed to create point.");
                return -2;
            }
            swModel.ClearSelection();

            SelectionMgr swSelMgr = (SelectionMgr)swModel.SelectionManager;
            SelectData swSelData = default(SelectData);
            swSelData = (SelectData)swSelMgr.CreateSelectData();

            status = swBody.Select2(false, swSelData);
            if (!status)
            {
                Console.WriteLine("Failed to select main body.");
                Debug.Print("Failed to select main body.");
                return -2;
            }
            status = skPoint.Select4(true, swSelData);
            if (!status)
            {
                Debug.Print("Failed to select new point.");
                Console.WriteLine("Failed to select new point.");
                return -2;
            }
            // Selections complete, measure distance
            swMeasure = swModelDocExt.CreateMeasure();
            status = swMeasure.Calculate(null);  // Measurement returns distance in meters
            if (!status)
            {
                Debug.Print("Failed to measure.");
                Console.WriteLine("Failed to measure.");
                return -2;
            }

            // Delete newly made point
            swModel.ClearSelection();
            swSelData = (SelectData)swSelMgr.CreateSelectData();
            status = skPoint.Select4(true, swSelData);
            if (!status)
            {
                Debug.Print("Failed to select new point for deletion.");
                Console.WriteLine("Failed to select new point for deletion.");
                return -2;
            }
            status = swModelDocExt.DeleteSelection2((int)(swDeleteSelectionOptions_e.swDelete_Absorbed | swDeleteSelectionOptions_e.swDelete_Children | swDeleteSelectionOptions_e.swDelete_Advanced));
            if (!status)
            {
                Debug.Print("Failed to delete a point.");
            }

            if (swMeasure.Distance <= algorithm_parameter)
            {
                return 0;
            }

            // Use a ray to determine point membership
            double sys_tolerance = .0001;  // Meters I think
            double pmc_tolerance = .003;
            double[] point = { x, y, z };
            double[] vector = { 1.0, 1.0, 1.0 }; // Doesn't matter, any direction works
            IBody2[] body_arr = new IBody2[] { swBody as IBody2 };
            int num_inters = (int)swModelDocExt.RayIntersections(body_arr, (Object)point, (Object)vector, (int)(swRayPtsOpts_e.swRayPtsOptsTOPOLS | swRayPtsOpts_e.swRayPtsOptsENTRY_EXIT | swRayPtsOpts_e.swRayPtsOptsNORMALS), 0, 0, true);

            double[] details = (double[])swModel.GetRayIntersectionsPoints();

            if (details != null)
            {
                for (int i = 0; i < (int)Math.Floor((double)details.Length / 9); i++)
                {
                    if (details[9 * i + 2] % 4 >= 2 || details[9 * i + 2] >= 48)  // Checks if hit is 'grazing' or both entry and exit
                    {
                        num_inters -= 1;
                    }
                }
            }

            if (num_inters % 2 == 1) { return 1; } else { return -1; };
        }
    }

}
